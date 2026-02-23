from __future__ import annotations

from app.modules.template_generator.contracts import (
    BlockGeometry,
    BubbleConfig,
    BubblePlacement,
    QuestionItem,
    QuestionNumberPlacement,
)


def build_bubble_layout(
    block: BlockGeometry, bubble_config: BubbleConfig
) -> tuple[list[BubblePlacement], list[QuestionNumberPlacement], list[QuestionItem]]:
    bubbles: list[BubblePlacement] = []
    question_numbers: list[QuestionNumberPlacement] = []
    question_items_map: dict[tuple[str, int], QuestionItem] = {}
    used_ids: set[str] = set()

    for group in bubble_config.groups:
        total_rows = group.num_questions if group.num_questions is not None else group.rows
        for row in range(total_rows):
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
                _validate_bubble_not_overlapping_existing(
                    center_x_mm=center_x,
                    center_y_mm=center_y,
                    radius_mm=group.radius_mm,
                    existing=bubbles,
                    group_id=group.group_id,
                )

                bubble_id = _build_bubble_id(group_id=group.group_id, row=row, col=col)
                if bubble_id in used_ids:
                    raise ValueError(f"duplicate bubble id '{bubble_id}' detected")
                used_ids.add(bubble_id)
                label = _resolve_label(group_labels=group.column_labels, col=col)
                if col == 0 and bubble_config.question_number_style.enabled:
                    question_number = QuestionNumberPlacement(
                        group_id=group.group_id,
                        row=row,
                        question_number=group.question_start_number + row,
                        center_x_mm=(center_x - bubble_config.question_number_style.center_gap_mm),
                        center_y_mm=center_y,
                    )
                    question_numbers.append(question_number)
                    question_items_map[(group.group_id, row)] = QuestionItem(
                        group_id=group.group_id,
                        row=row,
                        question_number=question_number.question_number,
                        number_center_x_mm=question_number.center_x_mm,
                        number_center_y_mm=question_number.center_y_mm,
                        options=[],
                    )

                bubble = BubblePlacement(
                    bubble_id=bubble_id,
                    group_id=group.group_id,
                    row=row,
                    col=col,
                    label=label,
                    center_x_mm=center_x,
                    center_y_mm=center_y,
                    radius_mm=group.radius_mm,
                )
                bubbles.append(bubble)
                if bubble_config.question_number_style.enabled:
                    question_items_map[(group.group_id, row)].options.append(bubble)

    question_items = [
        question_items_map[key]
        for key in sorted(
            question_items_map.keys(),
            key=lambda item: (item[0], item[1]),
        )
    ]
    for item in question_items:
        item.options.sort(key=lambda option: option.col)

    return bubbles, question_numbers, question_items


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


def _validate_bubble_not_overlapping_existing(
    center_x_mm: float,
    center_y_mm: float,
    radius_mm: float,
    existing: list[BubblePlacement],
    group_id: str,
) -> None:
    for bubble in existing:
        dx = center_x_mm - bubble.center_x_mm
        dy = center_y_mm - bubble.center_y_mm
        min_distance = radius_mm + bubble.radius_mm
        if (dx * dx + dy * dy) < (min_distance * min_distance):
            raise ValueError(
                f"bubble in group '{group_id}' overlaps bubble '{bubble.bubble_id}'"
            )


def _build_bubble_id(*, group_id: str, row: int, col: int) -> str:
    return f"{group_id}_{row:02d}_{col:02d}"


def _resolve_label(*, group_labels: list[str] | None, col: int) -> str:
    if group_labels is not None:
        return group_labels[col]
    return _excel_like_label(col)


def _excel_like_label(col: int) -> str:
    value = col
    label = ""
    while True:
        value, remainder = divmod(value, 26)
        label = chr(ord("A") + remainder) + label
        if value == 0:
            break
        value -= 1
    return label
