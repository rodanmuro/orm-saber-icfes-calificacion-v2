from __future__ import annotations

from app.modules.template_generator.aruco_renderer import build_aruco_layout
from app.modules.template_generator.bubble_layout import build_bubble_layout
from app.modules.template_generator.contracts import (
    AuxiliaryBlockConfig,
    BlockGeometry,
    MarkerPlacement,
    TemplateConfig,
    TemplateLayout,
)
from app.modules.template_generator.geometry import (
    compute_printable_area,
    is_rect_within_bounds,
    rectangles_overlap,
    square_from_center,
)


def build_template_layout(config: TemplateConfig) -> TemplateLayout:
    printable_area = compute_printable_area(config.page_config)

    block = BlockGeometry(
        x_mm=config.block_config.x_mm,
        y_mm=config.block_config.y_mm,
        width_mm=config.block_config.width_mm,
        height_mm=config.block_config.height_mm,
    )

    _validate_block_within_printable_area(block, printable_area)

    aruco_markers = build_aruco_layout(printable_area, config.aruco_config)
    _validate_aruco_layout(aruco_markers, printable_area, block)
    _validate_auxiliary_blocks(config.auxiliary_blocks, printable_area)
    bubbles, question_numbers, question_items = build_bubble_layout(block, config.bubble_config)

    return TemplateLayout(
        template_id=config.output_config.template_id,
        version=config.output_config.version,
        aruco_dictionary_name=config.aruco_config.dictionary_name,
        page=config.page_config,
        printable_area=printable_area,
        main_block_bbox=block,
        block=block,
        aruco_markers=aruco_markers,
        bubbles=bubbles,
        bubble_label_style=config.bubble_config.label_style,
        question_numbers=question_numbers,
        question_number_style=config.bubble_config.question_number_style,
        question_items=question_items,
        auxiliary_blocks=config.auxiliary_blocks,
    )


def _validate_block_within_printable_area(block: BlockGeometry, printable_area: BlockGeometry) -> None:
    if not is_rect_within_bounds(block, printable_area):
        raise ValueError("main block is outside printable area defined by margins")


def _validate_aruco_layout(
    markers: list[MarkerPlacement],
    printable_area: BlockGeometry,
    block: BlockGeometry,
) -> None:
    for marker in markers:
        marker_rect = square_from_center(
            center_x_mm=marker.center_x_mm,
            center_y_mm=marker.center_y_mm,
            size_mm=marker.size_mm,
        )
        if not is_rect_within_bounds(marker_rect, printable_area):
            raise ValueError(f"aruco marker '{marker.marker_id}' is outside printable area")
        if rectangles_overlap(marker_rect, block):
            raise ValueError(f"aruco marker '{marker.marker_id}' overlaps main block")


def _validate_auxiliary_blocks(
    blocks: list[AuxiliaryBlockConfig],
    printable_area: BlockGeometry,
) -> None:
    for item in blocks:
        rect = BlockGeometry(
            x_mm=item.x_mm,
            y_mm=item.y_mm,
            width_mm=item.width_mm,
            height_mm=item.height_mm,
        )
        if not is_rect_within_bounds(rect, printable_area):
            raise ValueError(
                f"auxiliary block '{item.block_id}' is outside printable area"
            )
