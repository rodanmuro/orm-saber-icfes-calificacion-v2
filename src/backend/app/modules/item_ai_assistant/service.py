from __future__ import annotations

from typing import Any

from app.modules.item_ai_assistant.domain import (
    GenerateItemDraftInput,
    GenerateItemDraftOutput,
    LLMProvider,
)
from app.modules.item_ai_assistant.errors import ItemAIAssistantValidationError
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
    options_doc = dict(validated["options_doc"])
    correct = validated["correct_answer"]
    if correct != "A":
        options_doc["A"], options_doc[correct] = options_doc[correct], options_doc["A"]
    return {
        "statement_doc": validated["statement_doc"],
        "options_doc": options_doc,
        "correct_answer": "A",
        "media_spec": validated.get("media_spec"),
    }


def _extract_usage(payload: dict[str, Any]) -> dict[str, int]:
    raw_usage = payload.get("__usage") if isinstance(payload, dict) else None
    if not isinstance(raw_usage, dict):
        return {
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }
    return {
        "input_tokens": int(raw_usage.get("input_tokens", 0) or 0),
        "cached_input_tokens": int(raw_usage.get("cached_input_tokens", 0) or 0),
        "output_tokens": int(raw_usage.get("output_tokens", 0) or 0),
        "total_tokens": int(raw_usage.get("total_tokens", 0) or 0),
    }


def _sum_usage(payloads: list[dict[str, Any]]) -> dict[str, int]:
    totals = {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }
    for payload in payloads:
        usage = _extract_usage(payload)
        for key in totals:
            totals[key] += int(usage.get(key, 0) or 0)
    return totals


def _build_usage_and_costs_from_usage(raw_usage: dict[str, int], model_name: str) -> dict[str, int | float | str]:
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


def _build_repair_prompt(original_user_prompt: str, validation_error: str) -> str:
    return (
        f"{original_user_prompt}\n\n"
        "Tu salida anterior no cumplio el formato requerido. "
        f"Error de validacion detectado: {validation_error}. "
        "Corrige y responde de nuevo SOLO JSON valido respetando exactamente el contrato."
    )


def generate_item_draft(
    payload: GenerateItemDraftInput,
    provider: LLMProvider | None = None,
) -> GenerateItemDraftOutput:
    validate_context(
        standard_name=payload.standard_name,
        competency_name=payload.competency_name,
    )

    llm_provider = provider or OpenAIItemDraftProvider()
    system_prompt = build_system_prompt()
    base_user_prompt = build_user_prompt(payload)

    attempts: list[dict[str, Any]] = []

    first_payload = llm_provider.generate_item_draft(
        system_prompt=system_prompt,
        user_prompt=base_user_prompt,
    )
    attempts.append(first_payload)

    try:
        validated = validate_model_output(first_payload)
        repaired = False
    except ItemAIAssistantValidationError as first_exc:
        second_payload = llm_provider.generate_item_draft(
            system_prompt=system_prompt,
            user_prompt=_build_repair_prompt(base_user_prompt, str(first_exc)),
        )
        attempts.append(second_payload)
        validated = validate_model_output(second_payload)
        repaired = True

    normalized = _normalize_correct_answer_to_a(validated)

    metadata: dict[str, str | bool] = {
        "ai_generated": True,
        "ai_model": llm_provider.model_name,
        "ai_prompt_version": PROMPT_VERSION,
        "ai_repaired": repaired,
    }
    usage = _build_usage_and_costs_from_usage(_sum_usage(attempts), llm_provider.model_name)

    return GenerateItemDraftOutput(
        statement_doc=normalized["statement_doc"],
        options_doc=normalized["options_doc"],
        correct_answer=normalized["correct_answer"],
        metadata=metadata,
        usage=usage,
        media_spec=normalized.get("media_spec"),
    )
