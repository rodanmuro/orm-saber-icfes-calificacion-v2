from __future__ import annotations

from app.modules.template_generator.aruco_renderer import build_aruco_layout
from app.modules.template_generator.contracts import ArucoConfig, BlockGeometry


def test_build_aruco_layout_applies_corner_offsets() -> None:
    printable_area = BlockGeometry(x_mm=10.0, y_mm=10.0, width_mm=100.0, height_mm=120.0)
    aruco_config = ArucoConfig.model_validate(
        {
            "dictionary_name": "DICT_4X4_50",
            "marker_size_mm": 10.0,
            "corner_inset_mm": 5.0,
            "ids": [0, 1, 2, 3],
            "corner_offsets_mm": {
                "top_left": {"x_mm": 1.0, "y_mm": 2.0},
                "top_right": {"x_mm": 3.0, "y_mm": 4.0},
                "bottom_left": {"x_mm": 5.0, "y_mm": 6.0},
                "bottom_right": {"x_mm": 7.0, "y_mm": 8.0},
            },
        }
    )

    markers = build_aruco_layout(printable_area, aruco_config)

    assert len(markers) == 4

    top_left, top_right, bottom_left, bottom_right = markers

    assert top_left.center_x_mm == 21.0
    assert top_left.center_y_mm == 22.0

    assert top_right.center_x_mm == 97.0
    assert top_right.center_y_mm == 24.0

    assert bottom_left.center_x_mm == 25.0
    assert bottom_left.center_y_mm == 114.0

    assert bottom_right.center_x_mm == 93.0
    assert bottom_right.center_y_mm == 112.0
