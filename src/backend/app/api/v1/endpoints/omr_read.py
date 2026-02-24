from __future__ import annotations

import json
import logging
import time

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.config import settings
from app.modules.omr_reader.api_service import (
    DEFAULT_METADATA_PATH,
    persist_omr_trace_json,
    persist_uploaded_image_bytes,
    resolve_reader_backend,
    run_omr_read_from_image_bytes,
)
from app.modules.omr_reader.errors import OMRReadInputError

router = APIRouter(prefix="/omr", tags=["omr"])
logger = logging.getLogger("uvicorn.error")


@router.post("/read-photo")
async def read_photo_omr(
    photo: UploadFile = File(...),
    metadata_path: str = Form(DEFAULT_METADATA_PATH),
    px_per_mm: float = Form(10.0),
    marked_threshold: float = Form(0.12),
    unmarked_threshold: float = Form(0.08),
    robust_mode: bool = Form(False),
    save_debug_artifacts: bool = Form(True),
) -> dict:
    try:
        request_start = time.perf_counter()
        configured_backend = resolve_reader_backend(None)
        if configured_backend == "gemini":
            logger.info("Enviando a Gemini | model=%s", settings.gemini_model)
        elif configured_backend == "openai":
            logger.info("Enviando a OpenAI | model=%s", settings.openai_model)
        else:
            logger.info("Procesando lectura OMR con motor=%s", configured_backend)

        image_bytes = await photo.read()
        uploaded_path = persist_uploaded_image_bytes(
            image_bytes=image_bytes,
            original_filename=photo.filename,
        )
        result = run_omr_read_from_image_bytes(
            image_bytes=image_bytes,
            metadata_path=metadata_path,
            px_per_mm=px_per_mm,
            marked_threshold=marked_threshold,
            unmarked_threshold=unmarked_threshold,
            robust_mode=robust_mode,
            save_debug_artifacts=save_debug_artifacts,
            debug_base_name=uploaded_path.stem,
        )
        trace_json_path = persist_omr_trace_json(
            uploaded_image_path=uploaded_path,
            result_payload=result,
        )
        result.setdefault("diagnostics", {})
        result["diagnostics"]["uploaded_image_path"] = str(uploaded_path)
        result["diagnostics"]["trace_json_path"] = str(trace_json_path)
        result["diagnostics"]["request_total_ms"] = round((time.perf_counter() - request_start) * 1000.0, 2)
        logger.info(
            "OMR read completed | template=%s version=%s summary=%s",
            result.get("template_id"),
            result.get("version"),
            json.dumps(result.get("quality_summary", {}), ensure_ascii=False),
        )
        logger.info("OMR image saved at: %s", uploaded_path)
        logger.info("OMR trace json saved at: %s", trace_json_path)
        diagnostics = result.get("diagnostics", {})
        engine = diagnostics.get("reader_backend", configured_backend)
        usage = diagnostics.get("gemini_usage", {})
        if engine == "openai":
            usage = diagnostics.get("openai_usage", usage)
        report = diagnostics.get("gemini_report", {})
        if engine == "openai":
            report = diagnostics.get("openai_report", report)
        gemini_latency_ms = diagnostics.get("gemini_model_latency_ms")
        if engine == "openai":
            gemini_latency_ms = diagnostics.get("openai_model_latency_ms")
        request_total_ms = diagnostics.get("request_total_ms")
        logger.info(
            "OMR engine=%s usage=%s report=%s gemini_model_latency_ms=%s request_total_ms=%s",
            engine,
            json.dumps(usage, ensure_ascii=False),
            json.dumps(report, ensure_ascii=False),
            gemini_latency_ms,
            request_total_ms,
        )
        lines: list[str] = []
        for item in result.get("questions", []):
            question_number = item.get("question_number")
            marked_options = item.get("marked_options", [])
            marked_text = ", ".join(marked_options) if marked_options else "-"
            lines.append(f"pregunta {question_number}: {marked_text}")

        logger.info("OMR respuestas leidas:\n%s", "\n".join(lines))
        return result
    except OMRReadInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"unexpected server error: {exc}",
        ) from exc
