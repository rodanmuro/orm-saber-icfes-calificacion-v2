from __future__ import annotations

from app.modules.template_generator.contracts import BlockGeometry, PageConfig


def compute_printable_area(page: PageConfig) -> BlockGeometry:
    return BlockGeometry(
        x_mm=page.margin_left_mm,
        y_mm=page.margin_top_mm,
        width_mm=page.width_mm - page.margin_left_mm - page.margin_right_mm,
        height_mm=page.height_mm - page.margin_top_mm - page.margin_bottom_mm,
    )


def is_rect_within_bounds(rect: BlockGeometry, bounds: BlockGeometry) -> bool:
    return (
        bounds.x_mm <= rect.x_mm
        and bounds.y_mm <= rect.y_mm
        and rect.x_mm + rect.width_mm <= bounds.x_mm + bounds.width_mm
        and rect.y_mm + rect.height_mm <= bounds.y_mm + bounds.height_mm
    )
