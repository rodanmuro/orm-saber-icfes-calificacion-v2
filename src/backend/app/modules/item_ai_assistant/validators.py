from __future__ import annotations

import re
from typing import Any

from app.modules.item_ai_assistant.errors import ItemAIAssistantValidationError

VALID_OPTION_KEYS = ("A", "B", "C", "D")
VALID_MEDIA_TARGETS = ("statement", "option_a", "option_b", "option_c", "option_d")
MAX_MEDIA_SPECS = 5


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


def _coerce_number(raw: Any) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)

    text = str(raw).strip()
    if not text:
        raise ValueError("empty numeric value")

    # Tolerar texto natural: "40%", "$1.800", "12,5", "valor=30".
    match = re.search(r"[-+]?\d[\d\.,]*", text)
    if not match:
        raise ValueError(f"no numeric token in {text!r}")

    token = match.group(0).replace(" ", "")

    # Caso 1: miles con punto y decimal con coma -> 1.234.567,89
    if re.fullmatch(r"[-+]?\d{1,3}(?:\.\d{3})+(?:,\d+)?", token):
        token = token.replace(".", "").replace(",", ".")
        return float(token)

    # Caso 2: miles con coma y decimal con punto -> 1,234,567.89
    if re.fullmatch(r"[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?", token):
        token = token.replace(",", "")
        return float(token)

    # Caso 3: solo coma (asumir decimal si hay 1-2 decimales, si no miles)
    if "," in token and "." not in token:
        left, right = token.split(",", 1)
        if right.isdigit() and len(right) <= 2:
            token = f"{left}.{right}"
        else:
            token = f"{left}{right}"
        return float(token)

    # Fallback: eliminar comas sueltas y parsear.
    token = token.replace(",", "")
    return float(token)


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
            numbers.append(_coerce_number(raw))
        except Exception as exc:  # noqa: BLE001
            raise ItemAIAssistantValidationError("media_spec contiene valores no numericos") from exc
    return numbers


def _normalize_data_pairs_to_labels_and_values(data_field: Any) -> tuple[list[str], list[float]]:
    if not isinstance(data_field, list):
        return [], []

    labels: list[str] = []
    values: list[float] = []

    for item in data_field:
        if not isinstance(item, dict):
            continue
        label_raw = item.get("label", "")
        value_raw = item.get("value", None)
        label = str(label_raw).strip()
        if not label:
            continue
        try:
            value = float(value_raw)
        except Exception as exc:  # noqa: BLE001
            raise ItemAIAssistantValidationError("media_spec.spec.data contiene valores no numericos") from exc
        labels.append(label)
        values.append(value)

    return labels, values


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

    # Compatibilidad: algunos modelos devuelven spec.data=[{label,value}] en lugar de labels/values|sizes.
    if isinstance(spec.get("data"), list):
        data_labels, data_values = _normalize_data_pairs_to_labels_and_values(spec.get("data"))
        if data_labels and data_values:
            if not labels:
                labels = data_labels
            if chart_type == "bar" and not spec.get("values"):
                normalized_spec["values"] = data_values
            if chart_type == "pie" and not spec.get("sizes"):
                normalized_spec["sizes"] = data_values

    if chart_type == "bar":
        values = _coerce_numeric_list(normalized_spec.get("values"))
        if not values:
            raise ItemAIAssistantValidationError("media_spec.spec.values invalido para bar")
        if not labels:
            raise ItemAIAssistantValidationError("media_spec.spec.labels requerido para bar")
        if len(values) != len(labels):
            raise ItemAIAssistantValidationError("media_spec.spec.labels y values deben coincidir en longitud")
        normalized_spec["labels"] = labels
        normalized_spec["values"] = values
    else:
        sizes = _coerce_numeric_list(normalized_spec.get("sizes"))
        if not sizes:
            sizes = _coerce_numeric_list(normalized_spec.get("values"))
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


def _validate_media_specs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_media_specs = payload.get("media_specs")
    raw_media_spec = payload.get("media_spec")

    if raw_media_specs is None and raw_media_spec is None:
        return []

    items: list[dict[str, Any]] = []

    if raw_media_specs is not None:
        if not isinstance(raw_media_specs, list):
            raise ItemAIAssistantValidationError("media_specs must be a list")
        for raw in raw_media_specs:
            if not isinstance(raw, dict):
                raise ItemAIAssistantValidationError("media_specs contiene elementos invalidos")
            items.append(raw)

    # Compatibilidad con contrato antiguo.
    if raw_media_spec is not None:
        if not isinstance(raw_media_spec, dict):
            raise ItemAIAssistantValidationError("media_spec must be null or an object")
        items.append(raw_media_spec)

    if not items:
        return []

    if len(items) > MAX_MEDIA_SPECS:
        raise ItemAIAssistantValidationError(f"media_specs supera el maximo permitido ({MAX_MEDIA_SPECS})")

    normalized: list[dict[str, Any]] = []
    used_targets: set[str] = set()

    for raw in items:
        normalized_item = _validate_chart_media_spec(raw)
        target = normalized_item["target"]
        if target in used_targets:
            raise ItemAIAssistantValidationError("media_specs contiene targets duplicados")
        used_targets.add(target)
        normalized.append(normalized_item)

    return normalized


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

    media_specs = _validate_media_specs(payload)

    return {
        "statement_doc": statement_doc,
        "options_doc": normalized_options_doc,
        "correct_answer": normalized_correct,
        "media_specs": media_specs,
        "media_spec": media_specs[0] if media_specs else None,
    }
