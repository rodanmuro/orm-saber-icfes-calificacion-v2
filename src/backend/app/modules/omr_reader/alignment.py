from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from app.modules.omr_reader.contracts import OMRAlignmentResult
from app.modules.omr_reader.errors import (
    ArucoDetectionError,
    CaptureQualityError,
    HomographyError,
    InvalidMetadataError,
)

REQUIRED_ALIGNMENT_KEYS = {"aruco_dictionary_name", "page", "aruco_markers"}
CORNER_ORDER = ["top_left", "top_right", "bottom_right", "bottom_left"]


def align_image_to_template(
    *,
    image: np.ndarray,
    metadata: dict[str, Any],
    px_per_mm: float = 10.0,
) -> OMRAlignmentResult:
    if px_per_mm <= 0:
        raise HomographyError("px_per_mm must be > 0")

    _validate_alignment_metadata(metadata)

    dictionary_name = metadata["aruco_dictionary_name"]
    aruco_markers = metadata["aruco_markers"]

    detected_centers_by_id = _detect_marker_centers(image, dictionary_name)

    src_points = _build_src_points(aruco_markers, detected_centers_by_id)
    _validate_capture_quality(src_points, image.shape[1], image.shape[0])
    dst_points = _build_dst_points(aruco_markers, px_per_mm)

    homography = cv2.getPerspectiveTransform(src_points, dst_points)
    if homography is None:
        raise HomographyError("could not compute homography matrix")

    page_width_px = int(round(float(metadata["page"]["width_mm"]) * px_per_mm))
    page_height_px = int(round(float(metadata["page"]["height_mm"]) * px_per_mm))

    if page_width_px <= 0 or page_height_px <= 0:
        raise HomographyError("invalid output image size from metadata page dimensions")

    aligned = cv2.warpPerspective(image, homography, (page_width_px, page_height_px))

    return OMRAlignmentResult(
        aligned_image=aligned,
        homography=homography,
        detected_marker_ids=sorted(detected_centers_by_id.keys()),
        output_width_px=page_width_px,
        output_height_px=page_height_px,
    )


def _validate_alignment_metadata(metadata: dict[str, Any]) -> None:
    missing = REQUIRED_ALIGNMENT_KEYS - set(metadata.keys())
    if missing:
        raise InvalidMetadataError(
            f"metadata missing required keys for alignment: {sorted(missing)}"
        )

    markers = metadata.get("aruco_markers")
    if not isinstance(markers, list) or len(markers) != 4:
        raise InvalidMetadataError("metadata 'aruco_markers' must contain exactly 4 items")

    page = metadata.get("page")
    if not isinstance(page, dict):
        raise InvalidMetadataError("metadata 'page' must be an object")
    if "width_mm" not in page or "height_mm" not in page:
        raise InvalidMetadataError("metadata 'page' must contain width_mm and height_mm")


def _detect_marker_centers(image: np.ndarray, dictionary_name: str) -> dict[int, np.ndarray]:
    aruco_module = cv2.aruco
    if not hasattr(aruco_module, dictionary_name):
        raise ArucoDetectionError(f"unsupported aruco dictionary '{dictionary_name}'")

    dictionary_code = getattr(aruco_module, dictionary_name)
    dictionary = aruco_module.getPredefinedDictionary(dictionary_code)
    detector_params = aruco_module.DetectorParameters()
    detector = aruco_module.ArucoDetector(dictionary, detector_params)

    corners, ids, _ = detector.detectMarkers(image)

    if ids is None or len(ids) == 0:
        raise ArucoDetectionError("no aruco markers were detected in image")

    centers_by_id: dict[int, np.ndarray] = {}
    for marker_corners, marker_id in zip(corners, ids.flatten(), strict=False):
        points = marker_corners.reshape(4, 2)
        center = points.mean(axis=0)
        centers_by_id[int(marker_id)] = center.astype(np.float32)

    return centers_by_id


def _build_src_points(
    metadata_markers: list[dict[str, Any]],
    detected_centers_by_id: dict[int, np.ndarray],
) -> np.ndarray:
    metadata_by_corner = {item["corner"]: item for item in metadata_markers}

    src_points: list[np.ndarray] = []
    for corner in CORNER_ORDER:
        marker = metadata_by_corner.get(corner)
        if marker is None:
            raise InvalidMetadataError(f"metadata marker missing corner '{corner}'")
        marker_id = int(marker["marker_id"])
        if marker_id not in detected_centers_by_id:
            raise ArucoDetectionError(
                f"required marker id '{marker_id}' for corner '{corner}' was not detected"
            )
        src_points.append(detected_centers_by_id[marker_id])

    return np.array(src_points, dtype=np.float32)


def _build_dst_points(metadata_markers: list[dict[str, Any]], px_per_mm: float) -> np.ndarray:
    metadata_by_corner = {item["corner"]: item for item in metadata_markers}

    dst_points: list[np.ndarray] = []
    for corner in CORNER_ORDER:
        marker = metadata_by_corner.get(corner)
        if marker is None:
            raise InvalidMetadataError(f"metadata marker missing corner '{corner}'")
        dst_points.append(
            np.array(
                [float(marker["center_x_mm"]) * px_per_mm, float(marker["center_y_mm"]) * px_per_mm],
                dtype=np.float32,
            )
        )

    return np.array(dst_points, dtype=np.float32)


def _validate_capture_quality(src_points: np.ndarray, image_w: int, image_h: int) -> None:
    if image_w <= 0 or image_h <= 0:
        raise CaptureQualityError("invalid source image size")

    quad = src_points.reshape(4, 2).astype(np.float32)
    area = float(cv2.contourArea(quad))
    image_area = float(image_w * image_h)
    area_ratio = area / image_area if image_area > 0 else 0.0

    if area_ratio < 0.08:
        raise CaptureQualityError(
            f"capture area too small for reliable OMR (marker quad ratio={area_ratio:.4f})"
        )

    sides = []
    for i in range(4):
        p1 = quad[i]
        p2 = quad[(i + 1) % 4]
        sides.append(float(np.linalg.norm(p2 - p1)))

    min_side = min(sides)
    max_side = max(sides)
    if min_side <= 0:
        raise CaptureQualityError("invalid marker geometry (zero side length)")

    side_ratio = max_side / min_side
    if side_ratio > 3.0:
        raise CaptureQualityError(
            f"capture perspective too extreme (side ratio={side_ratio:.3f})"
        )
