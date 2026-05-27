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


def _normalize_group_key(value: str | None) -> str | None:
    normalized = str(value or "").strip()
    return normalized or None


def _build_question_blocks(exam_items: list[ExamItem]) -> list[list[ExamItem]]:
    ordered_items = sorted(exam_items, key=lambda row: row.order_position)
    grouped_rows: dict[str, list[ExamItem]] = {}

    for row in ordered_items:
        group_key = _normalize_group_key(getattr(row, "group_key", None))
        if group_key is None:
            continue
        if group_key not in grouped_rows:
            grouped_rows[group_key] = []
        grouped_rows[group_key].append(row)

    blocks: list[list[ExamItem]] = []
    used_group_keys: set[str] = set()
    for row in ordered_items:
        group_key = _normalize_group_key(getattr(row, "group_key", None))
        if group_key is None:
            blocks.append([row])
            continue
        if group_key in used_group_keys:
            continue
        blocks.append(grouped_rows[group_key])
        used_group_keys.add(group_key)
    return blocks


def publish_exam_version(
    exam_items: list[ExamItem],
    seed_shuffle: int,
    shuffle_questions: bool,
    shuffle_options: bool,
) -> PublishedVersionResult:
    if not exam_items:
        raise ValueError("exam must contain at least one item")

    rng = random.Random(seed_shuffle)
    ordered_blocks = _build_question_blocks(exam_items)
    if shuffle_questions:
        rng.shuffle(ordered_blocks)

    ordered_items = [row for block in ordered_blocks for row in block]

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
