from __future__ import annotations

import random
from dataclasses import dataclass

from app.db.models import ExamItem

CHOICES = ["A", "B", "C", "D"]


@dataclass
class PublishedVersionRow:
    question_number: int
    source_exam_item_id: int
    item_id: int
    option_map: dict[str, str]
    correct_answer_original: str
    correct_answer_mapped: str


@dataclass
class PublishedVersionResult:
    answer_key: dict[str, str]
    rows: list[PublishedVersionRow]


def _build_option_map(rng: random.Random, shuffle_options: bool) -> dict[str, str]:
    if not shuffle_options:
        return {choice: choice for choice in CHOICES}

    shuffled = CHOICES[:]
    rng.shuffle(shuffled)
    return {original: mapped for original, mapped in zip(CHOICES, shuffled)}


def publish_exam_version(
    exam_items: list[ExamItem],
    seed_shuffle: int,
    shuffle_questions: bool,
    shuffle_options: bool,
) -> PublishedVersionResult:
    if not exam_items:
        raise ValueError("exam must contain at least one item")

    rng = random.Random(seed_shuffle)
    ordered_items = sorted(exam_items, key=lambda row: row.order_position)
    if shuffle_questions:
        rng.shuffle(ordered_items)

    rows: list[PublishedVersionRow] = []
    answer_key: dict[str, str] = {}

    for index, row in enumerate(ordered_items, start=1):
        original = row.item.correct_answer
        option_map = _build_option_map(rng=rng, shuffle_options=shuffle_options)
        mapped = option_map[original]

        rows.append(
            PublishedVersionRow(
                question_number=index,
                source_exam_item_id=row.id,
                item_id=row.item_id,
                option_map=option_map,
                correct_answer_original=original,
                correct_answer_mapped=mapped,
            )
        )
        answer_key[str(index)] = mapped

    return PublishedVersionResult(answer_key=answer_key, rows=rows)
