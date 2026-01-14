from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Type, TypeVar

from openai.types.responses.easy_input_message_param import EasyInputMessageParam
from pydantic import BaseModel, Field

StructuredSchemaT = TypeVar("StructuredSchemaT", bound=BaseModel)


@dataclass
class ChatMessage:
    role: Literal["user", "assistant", "system"]
    content: str

    def to_openai_message(self) -> EasyInputMessageParam:
        return EasyInputMessageParam(
            role=self.role, content=self.content, type="message"
        )


@dataclass
class ChatHistory:
    messages: list[ChatMessage]

    def append(self, message: ChatMessage) -> None:
        self.messages.append(message)

    def to_openai_message_history(self) -> list[Any]:
        return [message.to_openai_message() for message in self.messages]


class BaseLLM(ABC):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate_content(
        self,
        schema: Type[StructuredSchemaT],
    ) -> StructuredSchemaT | None: ...


class InvestmentSheetAnalysis(BaseModel):
    """Analysis for an investment spreadsheet"""

    general_trend: str = Field(description="General trend for the investements")
    best_performing: str = Field(
        description="Best performing investment and reasons for it"
    )
    worst_performing: str = Field(
        description="Worst performing investment and reasons for it"
    )
    suggestions: list[str] = Field(
        description="Suggestions on how to improve the portfolio, if any",
        default_factory=list,
    )

    def to_string(self) -> str:
        suggestions = "There are no suggestions on how to improve the portfolio"
        if self.suggestions:
            suggestions = "Suggestions to improve the portfolio:"
            for suggestion in self.suggestions:
                suggestions += "\n- " + suggestion
        return (
            f"The general trend of the investment is {self.general_trend}.\n"
            f"{self.best_performing}.\n"
            f"{self.worst_performing}.\n" + suggestions
        )
