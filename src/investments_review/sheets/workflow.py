import base64
import logging
from datetime import datetime
from typing import Annotated

import httpx
import pandas as pd
from jinja2 import Template
from llama_cloud import AsyncLlamaCloud
from workflows import Context, Workflow, step
from workflows.events import Event, StopEvent
from workflows.resource import Resource

from ..shared import FileEvent, FileUploadedEvent, get_llama_cloud_client
from .llm import OpenAILLM, get_llm
from .models import InvestmentSheetAnalysis
from .prompt import get_prompt


class SheetParsedEvent(Event):
    parquet_files: list[str]


class TableTransformationEvent(Event):
    markdown_tables: list[str]


class OutputEvent(StopEvent):
    final_result: str | None = None
    error: str | None = None


class SheetWorkflow(Workflow):
    @step
    async def upload_file_to_llamacloud(
        self,
        ev: FileEvent,
        ctx: Context,
        llama_cloud_client: Annotated[
            AsyncLlamaCloud, Resource(get_llama_cloud_client)
        ],
    ) -> FileUploadedEvent:
        logging.info("Starting to upload excel sheet to LlamaCloud")
        if not ev.is_source_content:
            file_obj = await llama_cloud_client.files.create(
                file=ev.file_input,
                purpose="parse",
                external_file_id=ev.file_input,
            )
        else:
            decoded = base64.b64decode(ev.file_input)
            file_name = (
                ev.file_name
                or datetime.now().isoformat().replace(":", "-").replace(".", "-")
                + ev.file_extension
            )
            mimetype = (
                "application/pdf"
                if ev.file_extension == ".pdf"
                else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            file_input = (file_name, decoded, mimetype)
            file_obj = await llama_cloud_client.files.create(
                file=file_input,
                purpose="parse",
                external_file_id=file_name,
            )
        event = FileUploadedEvent(file_id=file_obj.id)
        ctx.write_event_to_stream(event)
        logging.info("Finished uploading excel sheet to LlamaCloud")
        return event

    @step
    async def parse_sheet_file(
        self,
        ev: FileUploadedEvent,
        ctx: Context,
        llama_cloud_client: Annotated[
            AsyncLlamaCloud, Resource(get_llama_cloud_client)
        ],
    ) -> SheetParsedEvent | OutputEvent:
        logging.info("Starting to parse excel sheet...")
        result = await llama_cloud_client.beta.sheets.parse(
            file_id=ev.file_id,
        )
        logging.info("Finished parsing excel sheet")
        file_paths = []
        if result.success:
            logging.info("Starting to download Parquet files...")
            assert result.regions is not None, (
                "Regions should have been extracted if the job was successfull"
            )
            for region in result.regions:
                assert region.region_id is not None, "Region should have an ID"
                parquet_region_resp = (
                    await llama_cloud_client.beta.sheets.get_result_table(
                        region_type=region.region_type,  # type: ignore
                        spreadsheet_job_id=result.id,
                        region_id=region.region_id,
                    )
                )

                url = parquet_region_resp.url
                async with httpx.AsyncClient() as httpx_client:
                    resp = await httpx_client.get(url)
                    file_path = f"./downloaded_region_{region.region_id}.parquet"
                    with open(
                        f"./downloaded_region_{region.region_id}.parquet", "wb"
                    ) as f:
                        f.write(resp.content)
                    file_paths.append(file_path)
            logging.info("Finished downloading Parquet files")
        else:
            return OutputEvent(error="Could not parse sheet file")

        if len(file_paths) > 0:
            event = SheetParsedEvent(parquet_files=file_paths)
            ctx.write_event_to_stream(event)
            return event
        return OutputEvent(error="Could not retrieve any parquet file")

    @step
    async def parquet_to_markdown_table(
        self,
        ev: SheetParsedEvent,
        ctx: Context,
    ) -> TableTransformationEvent | OutputEvent:
        tables = []
        logging.info("Starting to convert Parquet files to markdown tables...")
        for file in ev.parquet_files:
            try:
                df = pd.read_parquet(file)
                markdown_table = df.to_markdown()
                tables.append(markdown_table)
            except Exception as e:
                logging.error(f"Could not load {file} because of {e}. Skipping...")
        logging.info("Finished converting Parquet files to markdown tables")
        if len(tables) > 0:
            event = TableTransformationEvent(markdown_tables=tables)
            ctx.write_event_to_stream(event)
            return event

        return OutputEvent(error="Could not transform any of the parquet files")

    @step
    async def llm_generate(
        self,
        ev: TableTransformationEvent,
        ctx: Context,
        llm: Annotated[OpenAILLM, Resource(get_llm)],
        prompt: Annotated[Template, Resource(get_prompt)],
    ) -> OutputEvent:
        tables = "\n\n".join(ev.markdown_tables)
        user_prompt = prompt.render(tables=tables)
        logging.info("Generating LLM response...")
        llm.add_user_message(user_prompt)
        response = await llm.generate_content(schema=InvestmentSheetAnalysis)
        logging.info("Finished generating LLM response")
        if response is None:
            return OutputEvent(error="Could not generate investment analysis")
        return OutputEvent(final_result=response.to_string())


workflow = SheetWorkflow(timeout=600)
