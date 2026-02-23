from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from app.modules.omr_reader.alignment import align_image_to_template
from app.modules.omr_reader.bubble_classifier import classify_bubbles
from app.modules.omr_reader.errors import InvalidImageError, InvalidMetadataError
from app.modules.omr_reader.loader import load_read_metadata
from app.modules.omr_reader.result_builder import build_omr_read_result

DEFAULT_METADATA_PATH = "data/output/template_basica_omr_v1.json"


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


def resolve_backend_relative_path(path_value: str) -> Path:
    backend_root = Path(__file__).resolve().parents[3]
    candidate = Path(path_value)

    resolved = (backend_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    if not str(resolved).startswith(str(backend_root.resolve())):
        raise InvalidMetadataError("metadata_path must stay inside backend directory")
    return resolved

