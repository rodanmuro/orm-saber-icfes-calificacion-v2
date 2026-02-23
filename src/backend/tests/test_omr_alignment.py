from __future__ import annotations

import cv2
import numpy as np
import pytest

from app.modules.omr_reader.alignment import align_image_to_template, _validate_capture_quality
from app.modules.omr_reader.errors import ArucoDetectionError, CaptureQualityError, InvalidMetadataError


def _synthetic_metadata() -> dict:
    return {
        "aruco_dictionary_name": "DICT_4X4_50",
        "page": {"width_mm": 100.0, "height_mm": 120.0},
        "aruco_markers": [
            {
                "marker_id": 0,
                "corner": "top_left",
                "center_x_mm": 10.0,
                "center_y_mm": 10.0,
            },
            {
                "marker_id": 1,
                "corner": "top_right",
                "center_x_mm": 90.0,
                "center_y_mm": 10.0,
            },
            {
                "marker_id": 2,
                "corner": "bottom_left",
                "center_x_mm": 10.0,
                "center_y_mm": 110.0,
            },
            {
                "marker_id": 3,
                "corner": "bottom_right",
                "center_x_mm": 90.0,
                "center_y_mm": 110.0,
            },
        ],
    }


def _build_synthetic_aruco_image() -> np.ndarray:
    canvas = np.full((1200, 1000, 3), 255, dtype=np.uint8)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    marker_size = 120
    markers = [
        (0, 100, 100),
        (1, 780, 100),
        (2, 100, 980),
        (3, 780, 980),
    ]

    for marker_id, x, y in markers:
        marker = cv2.aruco.generateImageMarker(dictionary, marker_id, marker_size)
        marker_bgr = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)
        canvas[y : y + marker_size, x : x + marker_size] = marker_bgr

    return canvas


def test_align_image_to_template_success() -> None:
    image = _build_synthetic_aruco_image()
    metadata = _synthetic_metadata()

    result = align_image_to_template(image=image, metadata=metadata, px_per_mm=10.0)

    assert result.output_width_px == 1000
    assert result.output_height_px == 1200
    assert result.aligned_image.shape[1] == 1000
    assert result.aligned_image.shape[0] == 1200
    assert result.detected_marker_ids == [0, 1, 2, 3]


def test_align_image_to_template_fails_without_markers() -> None:
    image = np.full((600, 600, 3), 255, dtype=np.uint8)
    metadata = _synthetic_metadata()

    with pytest.raises(ArucoDetectionError, match="no aruco markers"):
        align_image_to_template(image=image, metadata=metadata, px_per_mm=10.0)


def test_align_image_to_template_fails_with_invalid_metadata() -> None:
    image = _build_synthetic_aruco_image()
    metadata = {"aruco_dictionary_name": "DICT_4X4_50"}

    with pytest.raises(InvalidMetadataError, match="missing required keys"):
        align_image_to_template(image=image, metadata=metadata, px_per_mm=10.0)


def test_validate_capture_quality_rejects_tiny_quad() -> None:
    src_points = np.array(
        [[10.0, 10.0], [30.0, 10.0], [30.0, 30.0], [10.0, 30.0]],
        dtype=np.float32,
    )
    with pytest.raises(CaptureQualityError, match="area too small"):
        _validate_capture_quality(src_points, image_w=2000, image_h=2000)
