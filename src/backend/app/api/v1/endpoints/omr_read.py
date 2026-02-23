from __future__ import annotations

import json
import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.modules.omr_reader.api_service import (
    DEFAULT_METADATA_PATH,
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
    marked_threshold: float = Form(0.33),
    unmarked_threshold: float = Form(0.18),
) -> dict:
    try:
        image_bytes = await photo.read()
        result = run_omr_read_from_image_bytes(
            image_bytes=image_bytes,
            metadata_path=metadata_path,
            px_per_mm=px_per_mm,
            marked_threshold=marked_threshold,
            unmarked_threshold=unmarked_threshold,
        )
        logger.info(
            "OMR read completed | template=%s version=%s summary=%s",
            result.get("template_id"),
            result.get("version"),
            json.dumps(result.get("quality_summary", {}), ensure_ascii=False),
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
