from __future__ import annotations

from app.modules.template_generator.aruco_renderer import build_aruco_layout
from app.modules.template_generator.bubble_layout import build_bubble_layout
from app.modules.template_generator.contracts import BlockGeometry, TemplateConfig, TemplateLayout


def build_template_layout(config: TemplateConfig) -> TemplateLayout:
    _validate_block_within_page(config)

    block = BlockGeometry(
        x_mm=config.block_config.x_mm,
        y_mm=config.block_config.y_mm,
        width_mm=config.block_config.width_mm,
        height_mm=config.block_config.height_mm,
    )

    aruco_markers = build_aruco_layout(config.page_config, config.aruco_config)
    bubbles = build_bubble_layout(block, config.bubble_config)

    return TemplateLayout(
        template_id=config.output_config.template_id,
        version=config.output_config.version,
        page=config.page_config,
        block=block,
        aruco_markers=aruco_markers,
        bubbles=bubbles,
    )


def _validate_block_within_page(config: TemplateConfig) -> None:
    page = config.page_config
    block = config.block_config

    min_x = page.margin_left_mm
    min_y = page.margin_top_mm
    max_x = page.width_mm - page.margin_right_mm
    max_y = page.height_mm - page.margin_bottom_mm

    block_inside_page = (
        min_x <= block.x_mm
        and min_y <= block.y_mm
        and block.x_mm + block.width_mm <= max_x
        and block.y_mm + block.height_mm <= max_y
    )

    if not block_inside_page:
        raise ValueError("main block is outside printable area defined by margins")
