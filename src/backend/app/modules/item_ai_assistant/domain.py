from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class GenerateItemDraftInput:
    user_prompt: str
    standard_name: str
    competency_name: str
    subject: str | None = None
    difficulty: str | None = None
    ai_provider: str | None = None
    ai_model: str | None = None


@dataclass(frozen=True)
class GenerateItemDraftOutput:
    statement_doc: dict[str, Any]
    options_doc: dict[str, dict[str, Any]]
    correct_answer: str
    metadata: dict[str, str | bool]
    usage: dict[str, int | float | str] | None = None
    media_spec: dict[str, Any] | None = None
    media_specs: list[dict[str, Any]] | None = None


class LLMProvider(Protocol):
    model_name: str
    provider_name: str

    def generate_item_draft(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        ...
