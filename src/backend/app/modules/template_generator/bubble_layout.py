from __future__ import annotations

from app.modules.template_generator.contracts import BlockGeometry, BubbleConfig, BubblePlacement


def build_bubble_layout(block: BlockGeometry, bubble_config: BubbleConfig) -> list[BubblePlacement]:
    bubbles: list[BubblePlacement] = []

    for group in bubble_config.groups:
        for row in range(group.rows):
            for col in range(group.cols):
                center_x = block.x_mm + group.offset_x_mm + (col * group.spacing_x_mm)
                center_y = block.y_mm + group.offset_y_mm + (row * group.spacing_y_mm)

                _validate_bubble_inside_block(
                    center_x_mm=center_x,
                    center_y_mm=center_y,
                    radius_mm=group.radius_mm,
                    block=block,
                    group_id=group.group_id,
                )

                bubbles.append(
                    BubblePlacement(
                        bubble_id=f"{group.group_id}_{row:02d}_{col:02d}",
                        group_id=group.group_id,
                        row=row,
                        col=col,
                        center_x_mm=center_x,
                        center_y_mm=center_y,
                        radius_mm=group.radius_mm,
                    )
                )

    return bubbles


def _validate_bubble_inside_block(
    center_x_mm: float,
    center_y_mm: float,
    radius_mm: float,
    block: BlockGeometry,
    group_id: str,
) -> None:
    inside_horizontal = (block.x_mm <= center_x_mm - radius_mm) and (
        center_x_mm + radius_mm <= block.x_mm + block.width_mm
    )
    inside_vertical = (block.y_mm <= center_y_mm - radius_mm) and (
        center_y_mm + radius_mm <= block.y_mm + block.height_mm
    )

    if not (inside_horizontal and inside_vertical):
        raise ValueError(f"bubble in group '{group_id}' is outside main block bounds")
