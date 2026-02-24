from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from app.modules.omr_reader.alignment import align_image_to_template
from app.modules.omr_reader.errors import InvalidMetadataError


def prepare_llm_image_bytes(
    *,
    image: np.ndarray,
    metadata: dict[str, Any],
    px_per_mm: float,
) -> dict[str, Any]:
    aligned = align_image_to_template(
        image=image,
        metadata=metadata,
        px_per_mm=px_per_mm,
    )

    block = metadata.get("main_block_bbox") or metadata.get("block")
    if not isinstance(block, dict):
        raise InvalidMetadataError("metadata must include 'main_block_bbox' or 'block' for llm preprocessing")

    x_mm = float(block.get("x_mm", 0.0))
    y_mm = float(block.get("y_mm", 0.0))
    w_mm = float(block.get("width_mm", 0.0))
    h_mm = float(block.get("height_mm", 0.0))
    if w_mm <= 0 or h_mm <= 0:
        raise InvalidMetadataError("invalid block bbox dimensions for llm preprocessing")

    x = int(round(x_mm * px_per_mm))
    y = int(round(y_mm * px_per_mm))
    w = int(round(w_mm * px_per_mm))
    h = int(round(h_mm * px_per_mm))
    margin = int(round(2.0 * px_per_mm))

    img_h, img_w = aligned.aligned_image.shape[:2]
    x0 = max(0, x - margin)
    y0 = max(0, y - margin)
    x1 = min(img_w, x + w + margin)
    y1 = min(img_h, y + h + margin)
    if x1 <= x0 or y1 <= y0:
        raise InvalidMetadataError("computed crop bbox is invalid for llm preprocessing")

    crop = aligned.aligned_image[y0:y1, x0:x1]
    enhanced = _enhance_crop_for_llm(crop)

    ok, encoded = cv2.imencode(".jpg", enhanced, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    if not ok:
        raise InvalidMetadataError("failed to encode llm preprocessed image")

    return {
        "image_bytes": encoded.tobytes(),
        "diagnostics": {
            "detected_marker_ids": aligned.detected_marker_ids,
            "preprocess_method": "aruco_homography_block_crop_clahe",
            "crop_bbox_px": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
        },
    }


def _enhance_crop_for_llm(image_bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)
    merged = cv2.merge((l_enhanced, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
