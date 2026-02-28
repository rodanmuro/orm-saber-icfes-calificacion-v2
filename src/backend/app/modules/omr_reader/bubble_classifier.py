from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from app.modules.omr_reader.contracts import BubbleReadResult
from app.modules.omr_reader.errors import BubbleReadError, InvalidMetadataError

REQUIRED_BUBBLE_KEYS = {
    "bubble_id",
    "group_id",
    "row",
    "col",
    "label",
    "center_x_mm",
    "center_y_mm",
    "radius_mm",
}


def classify_bubbles(
    *,
    aligned_image: np.ndarray,
    metadata: dict[str, Any],
    px_per_mm: float = 10.0,
    marked_threshold: float = 0.45,
    unmarked_threshold: float = 0.35,
    inner_radius_factor: float = 0.58,
    robust_mode: bool = False,
    robust_contrast_alpha: float = 1.25,
    robust_contrast_beta: float = -8.0,
    debug_artifacts: dict[str, np.ndarray] | None = None,
) -> list[BubbleReadResult]:
    if px_per_mm <= 0:
        raise BubbleReadError("px_per_mm must be > 0")
    if not (0.0 <= unmarked_threshold <= marked_threshold <= 1.0):
        raise BubbleReadError("thresholds must satisfy 0 <= unmarked <= marked <= 1")
    if not (0.2 <= inner_radius_factor <= 1.0):
        raise BubbleReadError("inner_radius_factor must be between 0.2 and 1.0")
    if robust_contrast_alpha <= 0:
        raise BubbleReadError("robust_contrast_alpha must be > 0")

    bubbles = metadata.get("bubbles")
    if not isinstance(bubbles, list) or len(bubbles) == 0:
        raise InvalidMetadataError("metadata 'bubbles' must be a non-empty list")

    binary_inv = _build_binary_map(
        aligned_image=aligned_image,
        robust_mode=robust_mode,
        robust_contrast_alpha=robust_contrast_alpha,
        robust_contrast_beta=robust_contrast_beta,
    )
    if debug_artifacts is not None:
        debug_artifacts["binary_inv"] = binary_inv.copy()

    results: list[BubbleReadResult] = []
    for bubble in bubbles:
        _validate_bubble_metadata(bubble)

        cx = int(round(float(bubble["center_x_mm"]) * px_per_mm))
        cy = int(round(float(bubble["center_y_mm"]) * px_per_mm))
        radius_px = max(1, int(round(float(bubble["radius_mm"]) * px_per_mm)))
        inner_radius_px = max(1, int(round(radius_px * inner_radius_factor)))

        fill_ratio = _compute_fill_ratio(binary_inv, cx, cy, inner_radius_px)

        if fill_ratio >= marked_threshold:
            state = "marcada"
        elif fill_ratio <= unmarked_threshold:
            state = "no_marcada"
        else:
            state = "ambigua"

        results.append(
            BubbleReadResult(
                bubble_id=str(bubble["bubble_id"]),
                group_id=str(bubble["group_id"]),
                row=int(bubble["row"]),
                col=int(bubble["col"]),
                label=str(bubble["label"]),
                fill_ratio=float(fill_ratio),
                state=state,
            )
        )

    # Orden estable para trazabilidad reproducible.
    results.sort(key=lambda item: (item.group_id, item.row, item.col))
    return results


def _validate_bubble_metadata(bubble: dict[str, Any]) -> None:
    missing = REQUIRED_BUBBLE_KEYS - set(bubble.keys())
    if missing:
        raise InvalidMetadataError(f"bubble metadata missing keys: {sorted(missing)}")


def _build_binary_map(
    *,
    aligned_image: np.ndarray,
    robust_mode: bool,
    robust_contrast_alpha: float,
    robust_contrast_beta: float,
) -> np.ndarray:
    gray = cv2.cvtColor(aligned_image, cv2.COLOR_BGR2GRAY)

    if not robust_mode:
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary_inv = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return binary_inv

    # Robust pipeline for uneven lighting / glare:
    # 1) Background normalization
    # 2) Local contrast enhancement (CLAHE)
    # 3) Adaptive local threshold
    background = cv2.GaussianBlur(gray, (0, 0), sigmaX=35, sigmaY=35)
    normalized = cv2.divide(gray, background, scale=255)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(normalized)
    contrasted = cv2.convertScaleAbs(
        enhanced,
        alpha=robust_contrast_alpha,
        beta=robust_contrast_beta,
    )
    denoised = cv2.GaussianBlur(contrasted, (3, 3), 0)

    binary_inv = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        35,
        6,
    )
    return binary_inv


def _compute_fill_ratio(binary_inv: np.ndarray, cx: int, cy: int, radius: int) -> float:
    h, w = binary_inv.shape[:2]

    x0 = max(0, cx - radius)
    y0 = max(0, cy - radius)
    x1 = min(w, cx + radius + 1)
    y1 = min(h, cy + radius + 1)

    if x0 >= x1 or y0 >= y1:
        raise BubbleReadError("bubble ROI is outside aligned image bounds")

    roi = binary_inv[y0:y1, x0:x1]

    yy, xx = np.ogrid[y0:y1, x0:x1]
    mask = ((xx - cx) ** 2 + (yy - cy) ** 2) <= radius**2
    mask_count = int(mask.sum())
    if mask_count == 0:
        raise BubbleReadError("bubble mask has zero area")

    filled = int((roi[mask] > 0).sum())
    return filled / mask_count
