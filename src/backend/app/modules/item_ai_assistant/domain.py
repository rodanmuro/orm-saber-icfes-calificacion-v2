from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GenerateItemDraftInput:
    user_prompt: str
    standard_name: str
    competency_name: str
    subject: str | None = None
    difficulty: str | None = None


@dataclass(frozen=True)
class GenerateItemDraftOutput:
    statement: str
    options: dict[str, str]
    correct_answer: str
    metadata: dict[str, str | bool]
    usage: dict[str, int | float | str] | None = None


class LLMProvider(Protocol):
    model_name: str

    def generate_item_draft(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        ...
