from __future__ import annotations

import json
from datetime import datetime, timezone
import imghdr
from pathlib import Path
import time
from typing import Any

from app.core.config import settings
from app.modules.omr_reader.contracts import BubbleReadResult
from app.modules.omr_reader.errors import GeminiReadError
from app.modules.omr_reader.result_builder import build_omr_read_result


def ping_gemini_model() -> dict[str, Any]:
    if not settings.gemini_api_key:
        raise GeminiReadError("GEMINI_API_KEY is not configured")
    try:
        from google import genai
        from google.genai import types
    except Exception as exc:  # noqa: BLE001
        raise GeminiReadError(
            "google-genai dependency is missing. Install package 'google-genai' in backend environment."
        ) from exc

    client = genai.Client(api_key=settings.gemini_api_key)
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=["Respond only with: PONG"],
            config=types.GenerateContentConfig(
                response_mime_type="text/plain",
            ),
        )
    except Exception as exc:  # noqa: BLE001
        raise GeminiReadError(f"gemini ping failed: {exc}") from exc

    text = (response.text or "").strip()
    usage = _extract_gemini_usage(response)
    return {
        "ok": bool(text),
        "model": settings.gemini_model,
        "response_text": text,
        "usage": usage,
    }


def run_gemini_omr_read(
    *,
    image_bytes: bytes,
    metadata: dict[str, Any],
    metadata_file: Path,
    preprocess_diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not image_bytes:
        raise GeminiReadError("uploaded image is empty")
    if not settings.gemini_api_key:
        raise GeminiReadError("GEMINI_API_KEY is not configured")

    prompt = _build_prompt(metadata=metadata)
    gemini_response = _call_gemini(
        image_bytes=image_bytes,
        prompt=prompt,
        model=settings.gemini_model,
        api_key=settings.gemini_api_key,
        timeout_seconds=settings.gemini_timeout_seconds,
    )
    parsed = _parse_gemini_output(gemini_response["text"])
    bubble_results = _map_answers_to_bubble_results(
        metadata=metadata,
        answers=parsed["answers"],
    )

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
        "gemini_model": settings.gemini_model,
        "gemini_notes": parsed.get("notes"),
        "gemini_report": merged_report,
        "gemini_usage": gemini_response.get("usage"),
        "gemini_model_latency_ms": gemini_response.get("latency_ms"),
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
        "- La hoja tiene 4 marcadores ArUco, uno en cada esquina (superior izquierda, superior derecha, inferior izquierda, inferior derecha).\n"
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
        "\"report\":{"
        "\"ambiguous_questions\":[1,2],"
        "\"unreadable_questions\":[3],"
        "\"notes\":\"opcional\""
        "},"
        "\"notes\":\"opcional\""
        "}"
    )


def _call_gemini(
    *,
    image_bytes: bytes,
    prompt: str,
    model: str,
    api_key: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    try:
        from google import genai
        from google.genai import types
    except Exception as exc:  # noqa: BLE001
        raise GeminiReadError(
            "google-genai dependency is missing. Install package 'google-genai' in backend environment."
        ) from exc

    mime_type = _detect_mime_type(image_bytes)
    client = genai.Client(api_key=api_key)

    start = time.perf_counter()
    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
    except Exception as exc:  # noqa: BLE001
        raise GeminiReadError(f"gemini request failed: {exc}") from exc
    latency_ms = round((time.perf_counter() - start) * 1000.0, 2)

    try:
        text = response.text
    except Exception as exc:  # noqa: BLE001
        raise GeminiReadError("invalid gemini response structure") from exc
    return {"text": text, "usage": _extract_gemini_usage(response), "latency_ms": latency_ms}


def _extract_gemini_usage(response: Any) -> dict[str, Any]:
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return {}

    keys = [
        "prompt_token_count",
        "candidates_token_count",
        "total_token_count",
        "thoughts_token_count",
        "cached_content_token_count",
    ]
    out: dict[str, Any] = {}
    for key in keys:
        value = getattr(usage, key, None)
        if value is not None:
            out[key] = value

    # Best-effort fallback for SDK variants.
    if not out:
        try:
            if hasattr(usage, "model_dump"):
                dumped = usage.model_dump()
            elif hasattr(usage, "to_dict"):
                dumped = usage.to_dict()
            elif hasattr(usage, "__dict__"):
                dumped = dict(usage.__dict__)
            else:
                dumped = {}
            for key, value in dumped.items():
                if value is not None:
                    out[str(key)] = value
        except Exception:  # noqa: BLE001
            return {}
    return out


def _detect_mime_type(image_bytes: bytes) -> str:
    kind = imghdr.what(None, h=image_bytes)
    if kind == "jpeg":
        return "image/jpeg"
    if kind == "png":
        return "image/png"
    if kind == "webp":
        return "image/webp"
    return "image/jpeg"


def _parse_gemini_output(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GeminiReadError("gemini output is not valid JSON") from exc

    answers = payload.get("answers")
    if not isinstance(answers, list):
        raise GeminiReadError("gemini output missing 'answers' list")

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
        labels = []
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
