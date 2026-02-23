from __future__ import annotations

from app.modules.template_generator.contracts import BlockGeometry, PageConfig
from app.modules.template_generator.geometry import compute_printable_area, is_rect_within_bounds


def test_compute_printable_area() -> None:
    page = PageConfig(
        width_mm=215.9,
        height_mm=279.4,
        margin_top_mm=10.0,
        margin_right_mm=12.0,
        margin_bottom_mm=14.0,
        margin_left_mm=16.0,
    )

    area = compute_printable_area(page)

    assert area.x_mm == 16.0
    assert area.y_mm == 10.0
    assert area.width_mm == 215.9 - 16.0 - 12.0
    assert area.height_mm == 279.4 - 10.0 - 14.0


def test_is_rect_within_bounds_true_and_false() -> None:
    bounds = BlockGeometry(x_mm=10.0, y_mm=10.0, width_mm=100.0, height_mm=100.0)
    inside = BlockGeometry(x_mm=20.0, y_mm=20.0, width_mm=20.0, height_mm=20.0)
    outside = BlockGeometry(x_mm=5.0, y_mm=20.0, width_mm=20.0, height_mm=20.0)

    assert is_rect_within_bounds(inside, bounds)
    assert not is_rect_within_bounds(outside, bounds)
