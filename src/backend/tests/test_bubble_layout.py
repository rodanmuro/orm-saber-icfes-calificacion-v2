from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.modules.template_generator.bubble_layout import build_bubble_layout
from app.modules.template_generator.contracts import BlockGeometry, BubbleConfig, TemplateConfig


def test_bubble_layout_generates_stable_ids_and_positions() -> None:
    block = BlockGeometry(x_mm=10.0, y_mm=10.0, width_mm=100.0, height_mm=100.0)
    bubble_config = BubbleConfig.model_validate(
        {
            "groups": [
                {
                    "group_id": "G01",
                    "rows": 2,
                    "cols": 3,
                    "radius_mm": 2.0,
                    "spacing_x_mm": 10.0,
                    "spacing_y_mm": 10.0,
                    "offset_x_mm": 10.0,
                    "offset_y_mm": 10.0,
                }
            ]
        }
    )

    first, first_numbers, first_items = build_bubble_layout(block, bubble_config)
    second, second_numbers, second_items = build_bubble_layout(block, bubble_config)

    assert [b.bubble_id for b in first] == [b.bubble_id for b in second]
    assert [b.center_x_mm for b in first] == [b.center_x_mm for b in second]
    assert [b.center_y_mm for b in first] == [b.center_y_mm for b in second]
    assert [b.label for b in first[:3]] == ["A", "B", "C"]
    assert [q.question_number for q in first_numbers] == [1, 2]
    assert [q.question_number for q in first_numbers] == [
        q.question_number for q in second_numbers
    ]
    assert [item.question_number for item in first_items] == [1, 2]
    assert [len(item.options) for item in first_items] == [3, 3]
    assert [item.question_number for item in first_items] == [
        item.question_number for item in second_items
    ]


def test_bubble_layout_uses_custom_column_labels() -> None:
    block = BlockGeometry(x_mm=10.0, y_mm=10.0, width_mm=100.0, height_mm=100.0)
    bubble_config = BubbleConfig.model_validate(
        {
            "groups": [
                {
                    "group_id": "G01",
                    "rows": 1,
                    "cols": 4,
                    "radius_mm": 2.0,
                    "spacing_x_mm": 10.0,
                    "spacing_y_mm": 10.0,
                    "offset_x_mm": 10.0,
                    "offset_y_mm": 10.0,
                    "column_labels": ["A", "B", "C", "D"],
                }
            ]
        }
    )

    bubbles, _, _ = build_bubble_layout(block, bubble_config)
    assert [b.label for b in bubbles] == ["A", "B", "C", "D"]


def test_bubble_layout_rejects_overlapping_bubbles() -> None:
    block = BlockGeometry(x_mm=10.0, y_mm=10.0, width_mm=100.0, height_mm=100.0)
    bubble_config = BubbleConfig.model_validate(
        {
            "groups": [
                {
                    "group_id": "G01",
                    "rows": 1,
                    "cols": 2,
                    "radius_mm": 4.0,
                    "spacing_x_mm": 6.0,
                    "spacing_y_mm": 10.0,
                    "offset_x_mm": 10.0,
                    "offset_y_mm": 10.0,
                }
            ]
        }
    )

    with pytest.raises(ValueError, match="overlaps bubble"):
        build_bubble_layout(block, bubble_config)


def test_template_config_rejects_duplicate_bubble_group_ids(base_config_dict: dict) -> None:
    payload = dict(base_config_dict)
    payload["bubble_config"] = {
        "groups": [
            {
                "group_id": "G01",
                "rows": 1,
                "cols": 1,
                "radius_mm": 2.0,
                "spacing_x_mm": 10.0,
                "spacing_y_mm": 10.0,
                "offset_x_mm": 10.0,
                "offset_y_mm": 10.0,
            },
            {
                "group_id": "G01",
                "rows": 1,
                "cols": 1,
                "radius_mm": 2.0,
                "spacing_x_mm": 10.0,
                "spacing_y_mm": 10.0,
                "offset_x_mm": 30.0,
                "offset_y_mm": 10.0,
            },
        ]
    }

    with pytest.raises(ValidationError):
        TemplateConfig.model_validate(payload)


def test_bubble_layout_uses_num_questions_when_provided() -> None:
    block = BlockGeometry(x_mm=10.0, y_mm=10.0, width_mm=100.0, height_mm=100.0)
    bubble_config = BubbleConfig.model_validate(
        {
            "question_number_style": {
                "enabled": True,
                "center_gap_mm": 10.0,
            },
            "groups": [
                {
                    "group_id": "G01",
                    "rows": 2,
                    "num_questions": 3,
                    "question_start_number": 5,
                    "cols": 4,
                    "radius_mm": 2.0,
                    "spacing_x_mm": 10.0,
                    "spacing_y_mm": 10.0,
                    "offset_x_mm": 20.0,
                    "offset_y_mm": 20.0,
                    "column_labels": ["A", "B", "C", "D"],
                }
            ],
        }
    )

    bubbles, question_numbers, question_items = build_bubble_layout(block, bubble_config)

    assert len(bubbles) == 12
    assert [q.question_number for q in question_numbers] == [5, 6, 7]
    assert [item.question_number for item in question_items] == [5, 6, 7]
    assert all(len(item.options) == 4 for item in question_items)
    first_row_first_bubble = next(b for b in bubbles if b.row == 0 and b.col == 0)
    first_question = question_numbers[0]
    assert (first_row_first_bubble.center_x_mm - first_question.center_x_mm) == 10.0


def test_bubble_layout_fits_when_required_height_is_within_block() -> None:
    # Regla fisica: diametro 5mm => radio 2.5mm, separacion entre centros 10mm.
    num_questions = 15
    radius_mm = 2.5
    spacing_y_mm = 10.0
    offset_y_mm = 15.0
    required_height_mm = offset_y_mm + ((num_questions - 1) * spacing_y_mm) + radius_mm

    block = BlockGeometry(x_mm=10.0, y_mm=10.0, width_mm=120.0, height_mm=required_height_mm + 5.0)
    bubble_config = BubbleConfig.model_validate(
        {
            "groups": [
                {
                    "group_id": "G01",
                    "rows": num_questions,
                    "num_questions": num_questions,
                    "cols": 4,
                    "radius_mm": radius_mm,
                    "spacing_x_mm": 10.0,
                    "spacing_y_mm": spacing_y_mm,
                    "offset_x_mm": 20.0,
                    "offset_y_mm": offset_y_mm,
                    "column_labels": ["A", "B", "C", "D"],
                }
            ]
        }
    )

    bubbles, _, _ = build_bubble_layout(block, bubble_config)

    assert len(bubbles) == num_questions * 4


def test_bubble_layout_fails_when_required_height_exceeds_block() -> None:
    # Misma regla, pero forzando bloque insuficiente para validar fallo.
    num_questions = 15
    radius_mm = 2.5
    spacing_y_mm = 10.0
    offset_y_mm = 15.0
    required_height_mm = offset_y_mm + ((num_questions - 1) * spacing_y_mm) + radius_mm

    block = BlockGeometry(x_mm=10.0, y_mm=10.0, width_mm=120.0, height_mm=required_height_mm - 1.0)
    bubble_config = BubbleConfig.model_validate(
        {
            "groups": [
                {
                    "group_id": "G01",
                    "rows": num_questions,
                    "num_questions": num_questions,
                    "cols": 4,
                    "radius_mm": radius_mm,
                    "spacing_x_mm": 10.0,
                    "spacing_y_mm": spacing_y_mm,
                    "offset_x_mm": 20.0,
                    "offset_y_mm": offset_y_mm,
                    "column_labels": ["A", "B", "C", "D"],
                }
            ]
        }
    )

    with pytest.raises(ValueError, match="outside main block bounds"):
        build_bubble_layout(block, bubble_config)
