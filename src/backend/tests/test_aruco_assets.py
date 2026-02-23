from __future__ import annotations

import pytest
from reportlab.lib.utils import ImageReader

from app.modules.template_generator.aruco_assets import build_aruco_image_reader


def test_build_aruco_image_reader_success() -> None:
    image_reader = build_aruco_image_reader(
        dictionary_name="DICT_4X4_50",
        marker_id=1,
        marker_pixels=128,
    )

    assert isinstance(image_reader, ImageReader)


def test_build_aruco_image_reader_invalid_dictionary() -> None:
    with pytest.raises(ValueError, match="unsupported aruco dictionary"):
        build_aruco_image_reader(
            dictionary_name="DICT_FAKE",
            marker_id=1,
            marker_pixels=128,
        )
