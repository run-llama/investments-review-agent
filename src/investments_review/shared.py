import os
from typing import Literal

from llama_cloud import AsyncLlamaCloud
from workflows.events import Event, StartEvent


def get_llama_cloud_client() -> AsyncLlamaCloud:
    return AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))


class FileEvent(StartEvent):
    file_input: str
    file_name: str | None = None
    file_extension: Literal[".xlsx", ".pdf"] = ".pdf"
    is_source_content: bool


class FileUploadedEvent(Event):
    file_id: str
