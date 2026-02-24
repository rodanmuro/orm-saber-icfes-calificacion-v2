from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any

from app.core.config import settings
from app.modules.omr_reader.contracts import BubbleReadResult
from app.modules.omr_reader.errors import OpenAIReadError
from app.modules.omr_reader.result_builder import build_omr_read_result


def run_openai_omr_read(
    *,
    image_bytes: bytes,
    metadata: dict[str, Any],
    metadata_file: Path,
    preprocess_diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not image_bytes:
        raise OpenAIReadError("uploaded image is empty")
    if not settings.openai_api_key:
        raise OpenAIReadError("OPENAI_API_KEY is not configured")

    prompt = _build_prompt(metadata=metadata)
    openai_response = _call_openai(
        image_bytes=image_bytes,
        prompt=prompt,
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )
    parsed = _parse_output(openai_response["text"])
    bubble_results = _map_answers_to_bubble_results(metadata=metadata, answers=parsed["answers"])

    payload = build_omr_read_result(
        metadata=metadata,
        bubble_results=bubble_results,
        timestamp_iso=datetime.now(tz=timezone.utc).isoformat(),
    )
    auto_unreadable = sorted(
        int(q.get("question_number", -1))
        for q in payload.get("questions", [])
        if isinstance(q, dict) and len(q.get("marked_options", [])) == 0 and int(q.get("question_number", -1)) > 0
    )
    base_report = parsed.get("report", {}) if isinstance(parsed.get("report"), dict) else {}
    base_ambiguous = _normalize_question_id_list(base_report.get("ambiguous_questions"))
    base_unreadable = _normalize_question_id_list(base_report.get("unreadable_questions"))
    merged_report = {
        "ambiguous_questions": sorted(set(base_ambiguous)),
        "unreadable_questions": sorted(set(base_unreadable) | set(auto_unreadable)),
        "notes": base_report.get("notes"),
    }

    payload["thresholds"] = {"marked": None, "unmarked": None}
    payload["diagnostics"] = {
        "metadata_path": str(metadata_file),
        "robust_mode": False,
        "openai_model": settings.openai_model,
        "openai_notes": parsed.get("notes"),
        "openai_report": merged_report,
        "openai_usage": openai_response.get("usage"),
        "openai_model_latency_ms": openai_response.get("latency_ms"),
        "llm_preprocess": preprocess_diagnostics or {},
    }
    return payload


def _build_prompt(*, metadata: dict[str, Any]) -> str:
    template_id = metadata.get("template_id", "template")
    version = metadata.get("version", "v1")
    return (
        "Eres un lector OMR. Analiza SOLO la hoja de respuestas y devuelve JSON valido sin texto adicional. "
        "No uses markdown, no uses ```.\n"
        "Reglas:\n"
        "- La hoja tiene 4 marcadores ArUco, uno en cada esquina.\n"
        "- Usa los ArUco de las esquinas para orientarte y leer la hoja en su posicion correcta.\n"
        "- Detecta preguntas y burbujas marcadas.\n"
        "- Opciones validas por pregunta: A, B, C, D.\n"
        "- Si no hay marca clara, devuelve lista vacia en marked_options.\n"
        "- Si hay varias marcadas, devuelve todas en marked_options.\n"
        '- Si una pregunta es ambigua o no legible, usa status="REVISAR".\n'
        "- Total de preguntas esperado: 30.\n"
        "Formato JSON obligatorio:\n"
        "{"
        f"\"template_id\":\"{template_id}\","
        f"\"version\":\"{version}\","
        "\"answers\":[{\"question_number\":1,\"marked_options\":[\"A\"],\"status\":\"OK\"}],"
        "\"report\":{\"ambiguous_questions\":[1],\"unreadable_questions\":[2],\"notes\":\"opcional\"},"
        "\"notes\":\"opcional\""
        "}"
    )


def _call_openai(
    *,
    image_bytes: bytes,
    prompt: str,
    model: str,
    api_key: str,
) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except Exception as exc:  # noqa: BLE001
        raise OpenAIReadError("openai dependency is missing. Install package 'openai'.") from exc

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    client = OpenAI(api_key=api_key)
    start = time.perf_counter()
    try:
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_b64}"},
                    ],
                }
            ],
        )
    except Exception as exc:  # noqa: BLE001
        raise OpenAIReadError(f"openai request failed: {exc}") from exc
    latency_ms = round((time.perf_counter() - start) * 1000.0, 2)
    text = (getattr(response, "output_text", None) or "").strip()
    if not text:
        raise OpenAIReadError("openai output is empty")
    return {"text": text, "usage": _extract_openai_usage(response), "latency_ms": latency_ms}


def _extract_openai_usage(response: Any) -> dict[str, Any]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    out: dict[str, Any] = {}
    for key in ["input_tokens", "output_tokens", "total_tokens"]:
        value = getattr(usage, key, None)
        if value is not None:
            out[key] = value
    # best-effort nested details
    input_details = getattr(usage, "input_tokens_details", None)
    output_details = getattr(usage, "output_tokens_details", None)
    if input_details is not None:
        out["input_tokens_details"] = _to_plain_dict(input_details)
    if output_details is not None:
        out["output_tokens_details"] = _to_plain_dict(output_details)
    return out


def _to_plain_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return {k: v for k, v in value.__dict__.items() if not k.startswith("_")}
    return {}


def _parse_output(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise OpenAIReadError("openai output is not valid JSON") from exc

    answers = payload.get("answers")
    if not isinstance(answers, list):
        raise OpenAIReadError("openai output missing 'answers' list")

    normalized_answers: list[dict[str, Any]] = []
    derived_ambiguous: set[int] = set()
    derived_unreadable: set[int] = set()
    for item in answers:
        if not isinstance(item, dict):
            continue
        qn = item.get("question_number")
        marked = item.get("marked_options", [])
        status = str(item.get("status", "OK")).strip().upper()
        if not isinstance(qn, int):
            continue
        if not isinstance(marked, list):
            marked = []
        labels: list[str] = []
        for label in marked:
            if isinstance(label, str):
                up = label.strip().upper()
                if up in {"A", "B", "C", "D"} and up not in labels:
                    labels.append(up)
        if status == "REVISAR":
            if len(labels) <= 1:
                derived_unreadable.add(qn)
            if len(labels) > 1:
                derived_ambiguous.add(qn)
        elif len(labels) > 1:
            derived_ambiguous.add(qn)
        normalized_answers.append({"question_number": qn, "marked_options": labels})

    report = payload.get("report")
    report_obj = report if isinstance(report, dict) else {}
    ambiguous = _normalize_question_id_list(report_obj.get("ambiguous_questions"))
    unreadable = _normalize_question_id_list(report_obj.get("unreadable_questions"))
    merged_report = {
        "ambiguous_questions": sorted(set(ambiguous) | derived_ambiguous),
        "unreadable_questions": sorted(set(unreadable) | derived_unreadable),
        "notes": report_obj.get("notes"),
    }
    return {"answers": normalized_answers, "notes": payload.get("notes"), "report": merged_report}


def _normalize_question_id_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []
    out: list[int] = []
    for item in value:
        if isinstance(item, int):
            out.append(item)
        elif isinstance(item, str) and item.strip().isdigit():
            out.append(int(item.strip()))
    return out


def _map_answers_to_bubble_results(
    *,
    metadata: dict[str, Any],
    answers: list[dict[str, Any]],
) -> list[BubbleReadResult]:
    answer_by_question = {
        int(item["question_number"]): set(item.get("marked_options", []))
        for item in answers
    }
    bubble_results: list[BubbleReadResult] = []
    for question in metadata.get("question_items", []):
        question_number = int(question.get("question_number", -1))
        marked = answer_by_question.get(question_number, set())
        for option in question.get("options", []):
            label = str(option.get("label", "")).upper()
            is_marked = label in marked
            bubble_results.append(
                BubbleReadResult(
                    bubble_id=str(option.get("bubble_id", "")),
                    group_id=str(option.get("group_id", question.get("group_id", ""))),
                    row=int(option.get("row", question.get("row", -1))),
                    col=int(option.get("col", -1)),
                    label=label,
                    fill_ratio=1.0 if is_marked else 0.0,
                    state="marcada" if is_marked else "no_marcada",
                )
            )
    return bubble_results
