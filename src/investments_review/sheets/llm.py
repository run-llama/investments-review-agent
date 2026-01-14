import os
from typing import Annotated, Type, cast

from openai import AsyncOpenAI
from pydantic import BaseModel, model_validator
from typing_extensions import Self
from workflows.resource import ResourceConfig

from .models import BaseLLM, ChatHistory, ChatMessage, StructuredSchemaT
from .retry import retry

DEFAULT_OPENAI_MODEL = "gpt-4.1"


class OpenAILLM(BaseLLM):
    def __init__(self, api_key: str, model: str | None = None) -> None:
        super().__init__(api_key, model or DEFAULT_OPENAI_MODEL)
        self._client = AsyncOpenAI(api_key=self.api_key)
        self.chat_history: ChatHistory = ChatHistory(messages=[])

    def add_user_message(self, prompt: str) -> None:
        self.chat_history.append(ChatMessage(role="user", content=prompt))

    @retry()
    async def generate_content(
        self, schema: Type[StructuredSchemaT]
    ) -> StructuredSchemaT | None:
        response = await self._client.responses.parse(
            text_format=schema,
            model=self.model,
            input=self.chat_history.to_openai_message_history(),
        )
        self.chat_history.append(
            ChatMessage(role="assistant", content=response.output_text)
        )
        return response.output_parsed


class OpenAILLMConfig(BaseModel):
    api_key: str | None = None
    llm_model: str | None = None

    @model_validator(mode="after")
    def validate_openai_config(self) -> Self:
        if self.api_key is None or self.api_key == "$OPENAI_API_KEY":
            self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key is None:
            raise ValueError("Could not find OPENAI_API_KEY in the environment")
        if self.llm_model is None:
            self.llm_model = DEFAULT_OPENAI_MODEL
        return self


def get_llm(
    config: Annotated[
        OpenAILLMConfig, ResourceConfig("config.json", path_selector="llm")
    ],
) -> OpenAILLM:
    return OpenAILLM(api_key=cast(str, config.api_key), model=config.llm_model)
