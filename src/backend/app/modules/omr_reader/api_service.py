from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import cv2
import numpy as np

from app.modules.omr_reader.alignment import align_image_to_template
from app.modules.omr_reader.bubble_classifier import classify_bubbles
from app.modules.omr_reader.errors import InvalidImageError, InvalidMetadataError
from app.modules.omr_reader.loader import load_read_metadata
from app.modules.omr_reader.result_builder import build_omr_read_result

DEFAULT_METADATA_PATH = "data/output/template_basica_omr_v1.json"
DEFAULT_UPLOADS_DIR = "data/input/mobile_uploads"


def run_omr_read_from_image_bytes(
    *,
    image_bytes: bytes,
    metadata_path: str = DEFAULT_METADATA_PATH,
    px_per_mm: float = 10.0,
    marked_threshold: float = 0.33,
    unmarked_threshold: float = 0.18,
) -> dict[str, Any]:
    metadata_file = resolve_backend_relative_path(metadata_path)
    metadata = load_read_metadata(metadata_file)
    image = decode_image_bytes(image_bytes=image_bytes)

    aligned = align_image_to_template(
        image=image,
        metadata=metadata,
        px_per_mm=px_per_mm,
    )
    bubbles = classify_bubbles(
        aligned_image=aligned.aligned_image,
        metadata=metadata,
        px_per_mm=px_per_mm,
        marked_threshold=marked_threshold,
        unmarked_threshold=unmarked_threshold,
    )
    result = build_omr_read_result(metadata=metadata, bubble_results=bubbles)
    result["thresholds"] = {
        "marked": marked_threshold,
        "unmarked": unmarked_threshold,
    }
    result["diagnostics"] = {
        "metadata_path": str(metadata_file),
        "detected_marker_ids": aligned.detected_marker_ids,
    }
    return result


def decode_image_bytes(*, image_bytes: bytes) -> np.ndarray:
    if not image_bytes:
        raise InvalidImageError("uploaded image is empty")

    np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImageError("uploaded file is not a valid image (jpg/png)")
    return image


def persist_uploaded_image_bytes(
    *,
    image_bytes: bytes,
    original_filename: str | None = None,
    uploads_dir: str = DEFAULT_UPLOADS_DIR,
) -> Path:
    uploads_path = resolve_backend_relative_path(uploads_dir)
    uploads_path.mkdir(parents=True, exist_ok=True)

    ext = ".jpg"
    if original_filename:
        candidate = Path(original_filename).suffix.lower()
        if candidate in {".jpg", ".jpeg", ".png", ".webp"}:
            ext = candidate

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"mobile_{stamp}_{uuid4().hex[:8]}{ext}"
    out_path = uploads_path / file_name
    out_path.write_bytes(image_bytes)
    return out_path


def persist_omr_trace_json(
    *,
    uploaded_image_path: Path,
    result_payload: dict[str, Any],
) -> Path:
    trace_path = uploaded_image_path.with_suffix(".result.json")

    answers_by_question: list[dict[str, Any]] = []
    for question in result_payload.get("questions", []):
        marked = list(question.get("marked_options", []))
        ambiguous = list(question.get("ambiguous_options", []))
        answers_by_question.append(
            {
                "question_number": question.get("question_number"),
                "marked_options": marked,
                "ambiguous_options": ambiguous,
                "status": (
                    "marked"
                    if marked
                    else "ambiguous"
                    if ambiguous
                    else "blank"
                ),
            }
        )

    trace_payload = {
        "template_id": result_payload.get("template_id"),
        "version": result_payload.get("version"),
        "timestamp": result_payload.get("timestamp"),
        "uploaded_image_path": str(uploaded_image_path),
        "quality_summary": result_payload.get("quality_summary", {}),
        "answers_by_question": answers_by_question,
    }
    trace_path.write_text(
        json.dumps(trace_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return trace_path


def resolve_backend_relative_path(path_value: str) -> Path:
    backend_root = Path(__file__).resolve().parents[3]
    candidate = Path(path_value)

    resolved = (backend_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    if not str(resolved).startswith(str(backend_root.resolve())):
        raise InvalidMetadataError("metadata_path must stay inside backend directory")
    return resolved
