from __future__ import annotations

from typing import Any

from app.modules.item_ai_assistant.errors import ItemAIAssistantValidationError

VALID_OPTION_KEYS = ("A", "B", "C", "D")
VALID_MEDIA_TARGETS = ("statement", "option_a", "option_b", "option_c", "option_d")


def validate_context(*, standard_name: str, competency_name: str) -> None:
    if not standard_name.strip() or not competency_name.strip():
        raise ItemAIAssistantValidationError(
            "standard_name and competency_name are required"
        )


def _is_valid_tiptap_doc(value: Any) -> bool:
    return isinstance(value, dict) and value.get("type") == "doc" and isinstance(value.get("content"), list)


def _split_text_list(raw: str) -> list[str]:
    normalized = raw.replace(";", ",").replace("\n", ",")
    parts = [p.strip() for p in normalized.split(",")]
    return [p for p in parts if p]


def _coerce_labels(value: Any) -> list[str]:
    if isinstance(value, list):
        labels = [str(v).strip() for v in value if str(v).strip()]
        return labels
    if isinstance(value, str):
        return _split_text_list(value)
    return []


def _coerce_numeric_list(value: Any) -> list[float]:
    raw_values: list[Any]
    if isinstance(value, list):
        raw_values = value
    elif isinstance(value, str):
        raw_values = _split_text_list(value)
    else:
        return []

    numbers: list[float] = []
    for raw in raw_values:
        try:
            numbers.append(float(raw))
        except Exception as exc:  # noqa: BLE001
            raise ItemAIAssistantValidationError("media_spec contiene valores no numericos") from exc
    return numbers


def _validate_chart_media_spec(media_spec: dict[str, Any]) -> dict[str, Any]:
    mode = media_spec.get("mode")
    target = media_spec.get("target")
    spec = media_spec.get("spec")

    if mode != "chart_deterministic":
        raise ItemAIAssistantValidationError("media_spec.mode debe ser chart_deterministic")
    if target not in VALID_MEDIA_TARGETS:
        raise ItemAIAssistantValidationError("media_spec.target invalido")
    if not isinstance(spec, dict):
        raise ItemAIAssistantValidationError("media_spec.spec debe ser un objeto")

    chart_type = str(spec.get("chart_type", "")).lower()
    if chart_type not in {"bar", "pie"}:
        raise ItemAIAssistantValidationError("media_spec.spec.chart_type debe ser bar o pie")

    labels = _coerce_labels(spec.get("labels"))

    normalized_spec: dict[str, Any] = dict(spec)
    normalized_spec["chart_type"] = chart_type

    if chart_type == "bar":
        values = _coerce_numeric_list(spec.get("values"))
        if not values:
            raise ItemAIAssistantValidationError("media_spec.spec.values invalido para bar")
        if not labels:
            labels = [f"C{i + 1}" for i in range(len(values))]
        if len(values) != len(labels):
            raise ItemAIAssistantValidationError("media_spec.spec.labels y values deben coincidir en longitud")
        normalized_spec["labels"] = labels
        normalized_spec["values"] = values
    else:
        sizes = _coerce_numeric_list(spec.get("sizes"))
        if not sizes:
            raise ItemAIAssistantValidationError("media_spec.spec.sizes invalido para pie")
        if not labels:
            labels = [f"S{i + 1}" for i in range(len(sizes))]
        if len(sizes) != len(labels):
            raise ItemAIAssistantValidationError("media_spec.spec.labels y sizes deben coincidir en longitud")
        normalized_spec["labels"] = labels
        normalized_spec["sizes"] = sizes

    return {
        "mode": "chart_deterministic",
        "target": target,
        "spec": normalized_spec,
    }


def validate_model_output(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ItemAIAssistantValidationError("model output must be a JSON object")

    statement_doc = payload.get("statement_doc")
    if not _is_valid_tiptap_doc(statement_doc):
        raise ItemAIAssistantValidationError(
            "statement_doc must be a valid TipTap doc object"
        )

    options_doc = payload.get("options_doc")
    if not isinstance(options_doc, dict):
        raise ItemAIAssistantValidationError("options_doc must be an object with A/B/C/D")

    keys = set(options_doc.keys())
    if keys != set(VALID_OPTION_KEYS):
        raise ItemAIAssistantValidationError("options_doc must contain exactly A, B, C and D")

    normalized_options_doc: dict[str, dict] = {}
    for key in VALID_OPTION_KEYS:
        value = options_doc.get(key)
        if not _is_valid_tiptap_doc(value):
            raise ItemAIAssistantValidationError(f"option {key} must be a valid TipTap doc")
        normalized_options_doc[key] = value

    correct_answer = payload.get("correct_answer")
    if not isinstance(correct_answer, str):
        raise ItemAIAssistantValidationError("correct_answer must be a string")

    normalized_correct = correct_answer.strip().upper()
    if normalized_correct not in VALID_OPTION_KEYS:
        raise ItemAIAssistantValidationError("correct_answer must be one of A, B, C or D")

    media_spec_raw = payload.get("media_spec")
    media_spec: dict[str, Any] | None
    if media_spec_raw is None:
        media_spec = None
    elif isinstance(media_spec_raw, dict):
        media_spec = _validate_chart_media_spec(media_spec_raw)
    else:
        raise ItemAIAssistantValidationError("media_spec must be null or an object")

    return {
        "statement_doc": statement_doc,
        "options_doc": normalized_options_doc,
        "correct_answer": normalized_correct,
        "media_spec": media_spec,
    }
