from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class GenerateItemAIPayload(BaseModel):
    user_prompt: str = Field(min_length=3)
    standard_name: str = Field(min_length=1)
    competency_name: str = Field(min_length=1)
    subject: str | None = None
    difficulty: str | None = None


class AIUsageCost(BaseModel):
    model: str
    input_tokens: int
    cached_input_tokens: int
    non_cached_input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost_usd: float
    cached_input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    pricing_input_per_1m_usd: float
    pricing_cached_input_per_1m_usd: float
    pricing_output_per_1m_usd: float


class ItemAIMediaSpec(BaseModel):
    mode: Literal["chart_deterministic"]
    target: Literal["statement", "option_a", "option_b", "option_c", "option_d"]
    spec: dict[str, Any]


class GenerateItemAIResponse(BaseModel):
    statement_doc: dict[str, Any]
    options_doc: dict[str, dict[str, Any]]
    correct_answer: str
    metadata: dict[str, str | bool]
    usage: AIUsageCost | None = None
    media_spec: ItemAIMediaSpec | None = None
    media_specs: list[ItemAIMediaSpec] = Field(default_factory=list)


class GenerateMediaPayload(BaseModel):
    teacher_id: int = Field(ge=1)
    mode: Literal["chart_deterministic"]
    target: Literal["statement", "option_a", "option_b", "option_c", "option_d"]
    spec: dict[str, Any]


class GenerateMediaResponse(BaseModel):
    asset: dict[str, Any]
    insert_doc: dict[str, Any]
    meta: dict[str, Any]
