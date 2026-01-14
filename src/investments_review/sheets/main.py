import asyncio
import logging
import sys

from .workflow import FileEvent, OutputEvent, workflow


async def run_workflow(input_file: str) -> OutputEvent:
    result = await workflow.run(
        start_event=FileEvent(file_input=input_file, is_source_content=False)
    )
    return result


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    if len(sys.argv) == 2:
        input_file = sys.argv[1]
        result = asyncio.run(run_workflow(input_file=input_file))
        if result.error is not None:
            print("An error occurred: ", result.error)
        else:
            print("Final response:\n", result.final_result)
    else:
        raise ValueError("You should provide exactly one file from command line")
