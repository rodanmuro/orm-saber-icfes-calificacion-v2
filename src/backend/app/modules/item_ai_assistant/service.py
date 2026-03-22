from __future__ import annotations

from app.modules.item_ai_assistant.domain import (
    GenerateItemDraftInput,
    GenerateItemDraftOutput,
    LLMProvider,
)
from app.modules.item_ai_assistant.prompt_builder import (
    PROMPT_VERSION,
    build_system_prompt,
    build_user_prompt,
)
from app.modules.item_ai_assistant.providers.openai_provider import OpenAIItemDraftProvider
from app.modules.item_ai_assistant.validators import validate_context, validate_model_output

INPUT_PRICE_PER_1M_USD = 1.25
CACHED_INPUT_PRICE_PER_1M_USD = 0.125
OUTPUT_PRICE_PER_1M_USD = 10.00


def _normalize_correct_answer_to_a(validated: dict) -> dict:
    options = dict(validated["options"])
    correct = validated["correct_answer"]
    if correct != "A":
        options["A"], options[correct] = options[correct], options["A"]
    return {
        "statement": validated["statement"],
        "options": options,
        "correct_answer": "A",
    }


def _build_usage_and_costs(raw_payload: dict, model_name: str) -> dict[str, int | float | str]:
    raw_usage = raw_payload.get("__usage") if isinstance(raw_payload, dict) else None
    if not isinstance(raw_usage, dict):
        raw_usage = {}

    input_tokens = int(raw_usage.get("input_tokens", 0) or 0)
    cached_input_tokens = int(raw_usage.get("cached_input_tokens", 0) or 0)
    output_tokens = int(raw_usage.get("output_tokens", 0) or 0)
    total_tokens = int(raw_usage.get("total_tokens", 0) or (input_tokens + output_tokens))

    non_cached_input_tokens = max(input_tokens - cached_input_tokens, 0)

    input_cost_usd = (non_cached_input_tokens / 1_000_000) * INPUT_PRICE_PER_1M_USD
    cached_input_cost_usd = (cached_input_tokens / 1_000_000) * CACHED_INPUT_PRICE_PER_1M_USD
    output_cost_usd = (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_1M_USD
    total_cost_usd = input_cost_usd + cached_input_cost_usd + output_cost_usd

    return {
        "model": model_name,
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "non_cached_input_tokens": non_cached_input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "input_cost_usd": input_cost_usd,
        "cached_input_cost_usd": cached_input_cost_usd,
        "output_cost_usd": output_cost_usd,
        "total_cost_usd": total_cost_usd,
        "pricing_input_per_1m_usd": INPUT_PRICE_PER_1M_USD,
        "pricing_cached_input_per_1m_usd": CACHED_INPUT_PRICE_PER_1M_USD,
        "pricing_output_per_1m_usd": OUTPUT_PRICE_PER_1M_USD,
    }


def generate_item_draft(
    payload: GenerateItemDraftInput,
    provider: LLMProvider | None = None,
) -> GenerateItemDraftOutput:
    validate_context(
        standard_name=payload.standard_name,
        competency_name=payload.competency_name,
    )

    llm_provider = provider or OpenAIItemDraftProvider()
    model_payload = llm_provider.generate_item_draft(
        system_prompt=build_system_prompt(),
        user_prompt=build_user_prompt(payload),
    )
    validated = validate_model_output(model_payload)
    normalized = _normalize_correct_answer_to_a(validated)

    metadata: dict[str, str | bool] = {
        "ai_generated": True,
        "ai_model": llm_provider.model_name,
        "ai_prompt_version": PROMPT_VERSION,
    }
    usage = _build_usage_and_costs(model_payload, llm_provider.model_name)

    return GenerateItemDraftOutput(
        statement=normalized["statement"],
        options=normalized["options"],
        correct_answer=normalized["correct_answer"],
        metadata=metadata,
        usage=usage,
    )
