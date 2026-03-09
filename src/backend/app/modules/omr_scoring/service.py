from __future__ import annotations

from typing import Any


def build_answer_key_from_exam_items(exam_items: list[Any]) -> list[dict[str, Any]]:
    answer_key: list[dict[str, Any]] = []
    for index, exam_item in enumerate(exam_items, start=1):
        answer_key.append(
            {
                "question_number": index,
                "order_position": int(exam_item.order_position),
                "item_id": int(exam_item.item_id),
                "correct_answer": str(exam_item.item.correct_answer),
            }
        )
    return answer_key


def grade_omr_questions(
    answer_key: list[dict[str, Any]],
    omr_questions: list[dict[str, Any]],
) -> dict[str, Any]:
    by_question: dict[int, dict[str, Any]] = {}
    for item in omr_questions:
        question_number = int(item.get("question_number", 0))
        by_question[question_number] = item

    details: list[dict[str, Any]] = []
    total = len(answer_key)
    correct = 0
    incorrect = 0
    blank = 0
    ambiguous = 0

    for key_row in answer_key:
        qn = int(key_row["question_number"])
        correct_answer = str(key_row["correct_answer"])
        omr_row = by_question.get(qn, {})
        marked_options = omr_row.get("marked_options", []) if isinstance(omr_row, dict) else []

        status = "blank"
        marked_answer: str | None = None

        if len(marked_options) == 1:
            marked_answer = str(marked_options[0])
            if marked_answer == correct_answer:
                status = "correct"
                correct += 1
            else:
                status = "incorrect"
                incorrect += 1
        elif len(marked_options) == 0:
            blank += 1
        else:
            status = "ambiguous"
            ambiguous += 1

        details.append(
            {
                "question_number": qn,
                "item_id": key_row["item_id"],
                "correct_answer": correct_answer,
                "marked_answer": marked_answer,
                "marked_options": marked_options,
                "status": status,
            }
        )

    score_percent = round((correct / total) * 100.0, 2) if total > 0 else 0.0

    return {
        "summary": {
            "total_questions": total,
            "correct": correct,
            "incorrect": incorrect,
            "blank": blank,
            "ambiguous": ambiguous,
            "score_percent": score_percent,
        },
        "details": details,
    }

