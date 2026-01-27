import base64
import logging
from datetime import datetime
from typing import Annotated

from llama_cloud import AsyncLlamaCloud
from llama_cloud.types.extraction.extract_config_param import ExtractConfigParam
from workflows import Context, Workflow, step
from workflows.events import Event, StopEvent
from workflows.resource import Resource

from ..shared import FileEvent, FileUploadedEvent, get_llama_cloud_client
from .models import BoardUpdateDeck, ManagementPresentation, rules


class ClassificationEvent(Event):
    category: str
    reasons: str


class ExtractionEvent(StopEvent):
    final_result: str | None = None
    error: str | None = None


class PresentationWorkflow(Workflow):
    @step
    async def upload_file_to_llamacloud(
        self,
        ev: FileEvent,
        ctx: Context,
        llama_cloud_client: Annotated[
            AsyncLlamaCloud, Resource(get_llama_cloud_client)
        ],
    ) -> FileUploadedEvent:
        logging.info("Starting to upload presentation file to LlamaCloud")
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
        async with ctx.store.edit_state() as state:
            state.file_id = file_obj.id
        event = FileUploadedEvent(file_id=file_obj.id)
        ctx.write_event_to_stream(event)
        logging.info("Finished uploading presentation file to LlamaCloud")
        return event

    @step
    async def classify_presentation_as(
        self,
        ev: FileUploadedEvent,
        ctx: Context,
        llama_cloud_client: Annotated[
            AsyncLlamaCloud, Resource(get_llama_cloud_client)
        ],
    ) -> ClassificationEvent | ExtractionEvent:
        logging.info("Starting to classify presentation file")
        result = await llama_cloud_client.classifier.classify(
            file_ids=[ev.file_id], rules=rules, mode="FAST"
        )
        logging.info("Finished classification")
        result_item = result.items[0]  # there is only one classified file
        if result_item.result is not None:
            assert result_item.result.type is not None, (
                "Classification type should not be None"
            )
            logging.info(f"Classified document as: {result_item.result.type}")
            event = ClassificationEvent(
                category=result_item.result.type,
                reasons=result_item.result.reasoning,
            )
            ctx.write_event_to_stream(event)
            return event
        else:
            return ExtractionEvent(error="Could not produce a classification")

    @step
    async def extract_details(
        self,
        ev: ClassificationEvent,
        ctx: Context,
        llama_cloud_client: Annotated[
            AsyncLlamaCloud, Resource(get_llama_cloud_client)
        ],
    ) -> ExtractionEvent:
        logging.info("Starting to extract details from presentation file")
        file_id = (await ctx.store.get_state()).file_id
        schema = BoardUpdateDeck
        if ev.category == "management_presentation":
            schema = ManagementPresentation
        result = await llama_cloud_client.extraction.extract(
            data_schema=schema.model_json_schema(),
            config=ExtractConfigParam(extraction_mode="FAST"),
            file_id=file_id,
        )
        logging.info("Finished extracting details from presentation file")
        if result.data is not None:
            assert isinstance(result.data, dict), "Data should be a dictionary"
            details = schema.model_validate(result.data)
            return ExtractionEvent(final_result=details.to_string())
        return ExtractionEvent(error="Could not extract details from document")


workflow = PresentationWorkflow(timeout=600)
