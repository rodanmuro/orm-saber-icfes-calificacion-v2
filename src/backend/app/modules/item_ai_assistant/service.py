from __future__ import annotations

import re
from typing import Any

from app.modules.item_ai_assistant.domain import (
    GenerateItemDraftInput,
    GenerateItemDraftOutput,
    LLMProvider,
)
from app.modules.item_ai_assistant.errors import (
    ItemAIAssistantProviderError,
    ItemAIAssistantValidationError,
)
from app.modules.item_ai_assistant.prompt_builder import (
    PROMPT_VERSION,
    build_system_prompt,
    build_user_prompt,
)
from app.modules.item_ai_assistant.providers.groq_provider import GroqItemDraftProvider
from app.modules.item_ai_assistant.providers.openai_provider import OpenAIItemDraftProvider
from app.modules.item_ai_assistant.validators import validate_context, validate_model_output
from app.core.config import settings

INPUT_PRICE_PER_1M_USD = 1.25
CACHED_INPUT_PRICE_PER_1M_USD = 0.125
OUTPUT_PRICE_PER_1M_USD = 10.00
MAX_SERVICE_REPAIR_ATTEMPTS = 3

TABLE_HINTS = (
    "tabla",
    "table",
    "tabular",
)

TARGET_TO_OPTION_KEY = {
    "option_a": "A",
    "option_b": "B",
    "option_c": "C",
    "option_d": "D",
}
OPTION_KEY_TO_TARGET = {v: k for k, v in TARGET_TO_OPTION_KEY.items()}


def _doc_contains_node_type(node: Any, expected_type: str) -> bool:
    if not isinstance(node, dict):
        return False
    if node.get("type") == expected_type:
        return True
    content = node.get("content")
    if isinstance(content, list):
        return any(_doc_contains_node_type(child, expected_type) for child in content)
    return False


def _requires_table_in_statement(user_prompt: str) -> bool:
    text = (user_prompt or "").lower()
    return any(hint in text for hint in TABLE_HINTS)


def _enforce_table_requirement(*, user_prompt: str, statement_doc: dict[str, Any]) -> None:
    if not _requires_table_in_statement(user_prompt):
        return
    if not _doc_contains_node_type(statement_doc, "table"):
        raise ItemAIAssistantValidationError(
            "Cuando se solicita tabla, statement_doc debe incluir un nodo table"
        )


def _paragraph_text(node: Any) -> str:
    if not isinstance(node, dict) or node.get("type") != "paragraph":
        return ""
    content = node.get("content")
    if not isinstance(content, list):
        return ""
    chunks: list[str] = []
    for part in content:
        if isinstance(part, dict) and part.get("type") == "text":
            text = part.get("text")
            if isinstance(text, str):
                chunks.append(text)
    return "".join(chunks).strip()


def _build_text_paragraph(text: str) -> dict[str, Any]:
    return {
        "type": "paragraph",
        "content": [{"type": "text", "text": text}],
    }


def _table_cell_node(cell_text: str, *, header: bool) -> dict[str, Any]:
    node_type = "tableHeader" if header else "tableCell"
    return {
        "type": node_type,
        "content": [_build_text_paragraph(cell_text)],
    }


def _is_empty_table_cell(cell: Any) -> bool:
    if not isinstance(cell, dict):
        return False
    if cell.get("type") not in {"tableCell", "tableHeader"}:
        return False

    content = cell.get("content")
    if not isinstance(content, list) or not content:
        return True

    for paragraph in content:
        if not isinstance(paragraph, dict):
            return False
        if paragraph.get("type") != "paragraph":
            return False
        para_content = paragraph.get("content")
        if not isinstance(para_content, list):
            continue
        for part in para_content:
            if not isinstance(part, dict):
                return False
            if part.get("type") != "text":
                return False
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                return False
    return True


def _trim_edge_empty_cells(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    trimmed = list(cells)
    while len(trimmed) > 1 and _is_empty_table_cell(trimmed[0]):
        trimmed.pop(0)
    while len(trimmed) > 1 and _is_empty_table_cell(trimmed[-1]):
        trimmed.pop()
    return trimmed


def _pad_table_row_cells(cells: list[dict[str, Any]], target_len: int) -> list[dict[str, Any]]:
    if len(cells) >= target_len:
        return cells[:target_len]

    base_type = "tableCell"
    if cells and cells[0].get("type") == "tableHeader":
        base_type = "tableHeader"

    padded = list(cells)
    while len(padded) < target_len:
        padded.append(
            {
                "type": base_type,
                "content": [_build_text_paragraph("")],
            }
        )
    return padded


def _normalize_table_node(table_node: dict[str, Any]) -> dict[str, Any]:
    rows = table_node.get("content")
    if not isinstance(rows, list):
        return table_node

    normalized_rows: list[dict[str, Any]] = []
    max_cols = 0

    for row in rows:
        if not isinstance(row, dict) or row.get("type") != "tableRow":
            normalized_rows.append(row)
            continue
        raw_cells = row.get("content")
        if not isinstance(raw_cells, list):
            normalized_rows.append(row)
            continue
        trimmed_cells = _trim_edge_empty_cells([c for c in raw_cells if isinstance(c, dict)])
        max_cols = max(max_cols, len(trimmed_cells))
        normalized_rows.append({**row, "content": trimmed_cells})

    if max_cols <= 0:
        return table_node

    balanced_rows: list[dict[str, Any]] = []
    for row in normalized_rows:
        if not isinstance(row, dict) or row.get("type") != "tableRow":
            balanced_rows.append(row)
            continue
        cells = row.get("content")
        if not isinstance(cells, list):
            balanced_rows.append(row)
            continue
        balanced_rows.append({**row, "content": _pad_table_row_cells(cells, max_cols)})

    return {**table_node, "content": balanced_rows}


def _normalize_tables_in_doc(node: Any) -> Any:
    if isinstance(node, list):
        return [_normalize_tables_in_doc(child) for child in node]
    if not isinstance(node, dict):
        return node

    out = dict(node)
    if "content" in out and isinstance(out.get("content"), list):
        out["content"] = [_normalize_tables_in_doc(child) for child in out["content"]]

    if out.get("type") == "table":
        out = _normalize_table_node(out)
    return out


def _try_extract_table_rows_from_plain_text(statement_doc: dict[str, Any]) -> tuple[list[str], list[tuple[str, str]]]:
    content = statement_doc.get("content")
    if not isinstance(content, list):
        return [], []

    kept_paragraphs: list[str] = []
    rows: list[tuple[str, str]] = []

    pattern = re.compile(r"^\s*(?:[•\-*]\s*)?([^:|]+?)\s*:\s*([0-9]+(?:[.,][0-9]+)?)\b")
    for node in content:
        text = _paragraph_text(node)
        if not text:
            continue
        match = pattern.match(text)
        if match:
            rows.append((match.group(1).strip(), match.group(2).strip()))
        else:
            kept_paragraphs.append(text)

    return kept_paragraphs, rows


def _coerce_table_if_requested(*, user_prompt: str, statement_doc: dict[str, Any]) -> dict[str, Any]:
    if not _requires_table_in_statement(user_prompt):
        return statement_doc
    if _doc_contains_node_type(statement_doc, "table"):
        return statement_doc

    intro_paragraphs, rows = _try_extract_table_rows_from_plain_text(statement_doc)
    if len(rows) < 2:
        return statement_doc

    table_rows: list[dict[str, Any]] = [
        {
            "type": "tableRow",
            "content": [
                _table_cell_node("Categoria", header=True),
                _table_cell_node("Valor", header=True),
            ],
        }
    ]
    for label, value in rows:
        table_rows.append(
            {
                "type": "tableRow",
                "content": [
                    _table_cell_node(label, header=False),
                    _table_cell_node(value, header=False),
                ],
            }
        )

    new_content: list[dict[str, Any]] = [_build_text_paragraph(p) for p in intro_paragraphs]
    new_content.append({"type": "table", "content": table_rows})
    return {
        "type": "doc",
        "content": new_content,
    }


_ACUTE_ESCAPE_MAP = {
    "a": "á",
    "e": "é",
    "i": "í",
    "o": "ó",
    "u": "ú",
    "A": "Á",
    "E": "É",
    "I": "Í",
    "O": "Ó",
    "U": "Ú",
    "n": "ń",
    "N": "Ń",
}


def _normalize_text_escapes(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        char = match.group(1)
        return _ACUTE_ESCAPE_MAP.get(char, char)

    return re.sub(r"\\'([aAeEiIoOuUnN])", repl, text)


def _normalize_text_escapes_in_doc(node: Any) -> Any:
    if isinstance(node, list):
        return [_normalize_text_escapes_in_doc(child) for child in node]
    if not isinstance(node, dict):
        return node

    node_type = node.get("type")
    out = dict(node)

    if node_type == "text" and isinstance(node.get("text"), str):
        out["text"] = _normalize_text_escapes(node["text"])

    if "content" in node and isinstance(node.get("content"), list):
        out["content"] = [_normalize_text_escapes_in_doc(child) for child in node["content"]]

    return out


def _normalize_text_escapes_in_payload(validated: dict[str, Any]) -> dict[str, Any]:
    statement_doc = _normalize_tables_in_doc(
        _normalize_text_escapes_in_doc(validated["statement_doc"])
    )
    options_doc = {
        key: _normalize_tables_in_doc(_normalize_text_escapes_in_doc(doc))
        for key, doc in validated["options_doc"].items()
    }
    return {
        **validated,
        "statement_doc": statement_doc,
        "options_doc": options_doc,
    }


def _minimal_option_doc() -> dict[str, Any]:
    return {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Observa la grafica."}],
            }
        ],
    }


def _swap_media_targets(media_specs: list[dict[str, Any]], key_a: str, key_b: str) -> list[dict[str, Any]]:
    target_a = OPTION_KEY_TO_TARGET.get(key_a)
    target_b = OPTION_KEY_TO_TARGET.get(key_b)
    if not target_a or not target_b:
        return media_specs

    swapped: list[dict[str, Any]] = []
    for item in media_specs:
        if not isinstance(item, dict):
            swapped.append(item)
            continue
        current_target = item.get("target")
        next_target = current_target
        if current_target == target_a:
            next_target = target_b
        elif current_target == target_b:
            next_target = target_a
        swapped.append({**item, "target": next_target})
    return swapped


def _normalize_options_for_media_targets(
    options_doc: dict[str, dict[str, Any]],
    media_specs: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    result = dict(options_doc)
    targets = {
        item.get("target")
        for item in media_specs
        if isinstance(item, dict) and isinstance(item.get("target"), str)
    }
    for target in targets:
        key = TARGET_TO_OPTION_KEY.get(target)
        if key:
            result[key] = _minimal_option_doc()
    return result


def _normalize_correct_answer_to_a(validated: dict) -> dict:
    options_doc = dict(validated["options_doc"])
    media_specs = list(validated.get("media_specs", []))
    correct = validated["correct_answer"]

    if correct != "A":
        options_doc["A"], options_doc[correct] = options_doc[correct], options_doc["A"]
        media_specs = _swap_media_targets(media_specs, "A", correct)

    options_doc = _normalize_options_for_media_targets(options_doc, media_specs)

    return {
        "statement_doc": validated["statement_doc"],
        "options_doc": options_doc,
        "correct_answer": "A",
        "media_spec": media_specs[0] if media_specs else None,
        "media_specs": media_specs,
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


def _build_usage_for_provider(
    raw_usage: dict[str, int],
    *,
    model_name: str,
    provider_name: str,
) -> dict[str, int | float | str]:
    if provider_name == "openai":
        return _build_usage_and_costs_from_usage(raw_usage, model_name)

    input_tokens = int(raw_usage.get("input_tokens", 0) or 0)
    cached_input_tokens = int(raw_usage.get("cached_input_tokens", 0) or 0)
    output_tokens = int(raw_usage.get("output_tokens", 0) or 0)
    total_tokens = int(raw_usage.get("total_tokens", 0) or (input_tokens + output_tokens))

    return {
        "provider": provider_name,
        "model": model_name,
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_input_tokens,
        "non_cached_input_tokens": max(input_tokens - cached_input_tokens, 0),
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "input_cost_usd": 0.0,
        "cached_input_cost_usd": 0.0,
        "output_cost_usd": 0.0,
        "total_cost_usd": 0.0,
        "pricing_input_per_1m_usd": 0.0,
        "pricing_cached_input_per_1m_usd": 0.0,
        "pricing_output_per_1m_usd": 0.0,
    }


def _build_default_provider(*, requested_provider: str | None = None, requested_model: str | None = None) -> LLMProvider:
    provider_name = (requested_provider or settings.ai_provider or "openai").strip().lower()
    model_name = (requested_model or "").strip() or None
    if provider_name == "groq":
        return GroqItemDraftProvider(model_name=model_name)
    if provider_name == "openai":
        return OpenAIItemDraftProvider(model_name=model_name)
    raise ItemAIAssistantProviderError(
        f"Unsupported AI provider '{provider_name}'. Use 'openai' or 'groq'."
    )


def _build_repair_prompt(original_user_prompt: str, validation_error: str) -> str:
    return (
        f"{original_user_prompt}\n\n"
        "Tu salida anterior no cumplio el formato requerido. "
        f"Error de validacion detectado: {validation_error}. "
        "Corrige y responde de nuevo SOLO JSON valido respetando exactamente el contrato."
    )


def _is_retryable_provider_output_error(exc: ItemAIAssistantProviderError) -> bool:
    text = str(exc).lower()
    return (
        "output is empty" in text
        or "output is not valid json" in text
    )


def _build_provider_repair_prompt(original_user_prompt: str, provider_error: str) -> str:
    return (
        f"{original_user_prompt}\n\n"
        "Tu salida anterior no fue util para procesar la respuesta. "
        f"Error detectado: {provider_error}. "
        "Responde SOLO con un JSON valido (sin markdown, sin texto adicional), "
        "cumpliendo exactamente el contrato requerido."
    )


def generate_item_draft(
    payload: GenerateItemDraftInput,
    provider: LLMProvider | None = None,
) -> GenerateItemDraftOutput:
    validate_context(
        standard_name=payload.standard_name,
        competency_name=payload.competency_name,
    )

    llm_provider = provider or _build_default_provider(
        requested_provider=payload.ai_provider,
        requested_model=payload.ai_model,
    )
    system_prompt = build_system_prompt()
    base_user_prompt = build_user_prompt(payload)

    attempts: list[dict[str, Any]] = []
    repaired = False
    current_prompt = base_user_prompt
    validated: dict[str, Any] | None = None
    last_validation_exc: ItemAIAssistantValidationError | None = None
    last_provider_exc: ItemAIAssistantProviderError | None = None

    for attempt_number in range(1, MAX_SERVICE_REPAIR_ATTEMPTS + 1):
        try:
            raw_payload = llm_provider.generate_item_draft(
                system_prompt=system_prompt,
                user_prompt=current_prompt,
            )
        except ItemAIAssistantProviderError as exc:
            last_provider_exc = exc
            if attempt_number >= MAX_SERVICE_REPAIR_ATTEMPTS or not _is_retryable_provider_output_error(exc):
                raise
            repaired = True
            current_prompt = _build_provider_repair_prompt(base_user_prompt, str(exc))
            continue

        attempts.append(raw_payload)
        try:
            validated_candidate = validate_model_output(raw_payload)
            validated_candidate = _normalize_text_escapes_in_payload(validated_candidate)
            validated_candidate["statement_doc"] = _coerce_table_if_requested(
                user_prompt=payload.user_prompt,
                statement_doc=validated_candidate["statement_doc"],
            )
            _enforce_table_requirement(
                user_prompt=payload.user_prompt,
                statement_doc=validated_candidate["statement_doc"],
            )
            validated = validated_candidate
            break
        except ItemAIAssistantValidationError as exc:
            last_validation_exc = exc
            if attempt_number >= MAX_SERVICE_REPAIR_ATTEMPTS:
                raise
            repaired = True
            current_prompt = _build_repair_prompt(base_user_prompt, str(exc))
            continue

    if validated is None:
        if last_validation_exc is not None:
            raise last_validation_exc
        if last_provider_exc is not None:
            raise last_provider_exc
        raise ItemAIAssistantValidationError("No fue posible validar la respuesta del proveedor IA")

    normalized = _normalize_correct_answer_to_a(validated)

    metadata: dict[str, str | bool] = {
        "ai_generated": True,
        "ai_model": llm_provider.model_name,
        "ai_prompt_version": PROMPT_VERSION,
        "ai_repaired": repaired,
    }
    usage = _build_usage_for_provider(
        _sum_usage(attempts),
        model_name=llm_provider.model_name,
        provider_name=getattr(llm_provider, "provider_name", "openai"),
    )

    return GenerateItemDraftOutput(
        statement_doc=normalized["statement_doc"],
        options_doc=normalized["options_doc"],
        correct_answer=normalized["correct_answer"],
        metadata=metadata,
        usage=usage,
        media_spec=normalized.get("media_spec"),
        media_specs=normalized.get("media_specs", []),
    )
