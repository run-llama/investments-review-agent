import os

from llama_cloud import AsyncLlamaCloud
from workflows.events import Event, StartEvent


def get_llama_cloud_client() -> AsyncLlamaCloud:
    return AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))


class FileEvent(StartEvent):
    file_path: str


class FileUploadedEvent(Event):
    file_id: str
