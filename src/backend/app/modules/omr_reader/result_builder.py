from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.modules.omr_reader.contracts import BubbleReadResult
from app.modules.omr_reader.errors import BubbleReadError, InvalidMetadataError


def build_omr_read_result(
    *,
    metadata: dict[str, Any],
    bubble_results: list[BubbleReadResult],
    timestamp_iso: str | None = None,
) -> dict[str, Any]:
    question_items = metadata.get("question_items")
    if not isinstance(question_items, list) or len(question_items) == 0:
        raise InvalidMetadataError("metadata 'question_items' must be a non-empty list")

    bubble_by_id: dict[str, BubbleReadResult] = {}
    for item in bubble_results:
        if item.bubble_id in bubble_by_id:
            raise BubbleReadError(f"duplicate bubble result detected: {item.bubble_id}")
        bubble_by_id[item.bubble_id] = item

        questions_payload: list[dict[str, Any]] = []
    expected_option_count = 0
    referenced_bubble_ids: set[str] = set()

    for question in question_items:
        options = question.get("options")
        if not isinstance(options, list) or len(options) == 0:
            raise InvalidMetadataError("each question item must define a non-empty 'options' list")

        question_options: list[dict[str, Any]] = []
        marked_options: list[str] = []
        ambiguous_options: list[str] = []

        for option in options:
            bubble_id = str(option.get("bubble_id", ""))
            label = str(option.get("label", ""))
            if not bubble_id:
                raise InvalidMetadataError("question option is missing 'bubble_id'")
            if bubble_id in referenced_bubble_ids:
                raise InvalidMetadataError(f"duplicate bubble_id in question_items: {bubble_id}")
            referenced_bubble_ids.add(bubble_id)

            bubble_result = bubble_by_id.get(bubble_id)
            if bubble_result is None:
                raise BubbleReadError(
                    f"missing bubble result for question option bubble_id={bubble_id}"
                )

            option_payload = {
                "bubble_id": bubble_result.bubble_id,
                "label": label or bubble_result.label,
                "state": bubble_result.state,
                "fill_ratio": round(float(bubble_result.fill_ratio), 6),
            }
            question_options.append(option_payload)
            expected_option_count += 1

            if bubble_result.state == "marcada":
                marked_options.append(option_payload["label"])
            elif bubble_result.state == "ambigua":
                ambiguous_options.append(option_payload["label"])

        if len(marked_options) > 1:
            marked_option_payloads = [item for item in question_options if item["state"] == "marcada"]
            winner = max(marked_option_payloads, key=lambda item: float(item["fill_ratio"]))
            winner_label = winner["label"]
            for item in marked_option_payloads:
                if item["label"] != winner_label:
                    item["state"] = "ambigua"
                    if item["label"] not in ambiguous_options:
                        ambiguous_options.append(item["label"])
            marked_options = [winner_label]

        questions_payload.append(
            {
                "question_number": int(question.get("question_number", -1)),
                "group_id": str(question.get("group_id", "")),
                "row": int(question.get("row", -1)),
                "options": question_options,
                "marked_options": marked_options,
                "ambiguous_options": ambiguous_options,
            }
        )

    extra_results = sorted(set(bubble_by_id.keys()) - referenced_bubble_ids)
    if extra_results:
        raise BubbleReadError(
            "bubble results contain ids not present in metadata question_items: "
            + ", ".join(extra_results[:5])
        )

    reported_option_count = len(bubble_results)
    if expected_option_count != reported_option_count:
        raise BubbleReadError(
            "bubble count mismatch: "
            f"expected={expected_option_count}, reported={reported_option_count}"
        )

    marked_count = sum(
        1 for q in questions_payload for option in q["options"] if option["state"] == "marcada"
    )
    unmarked_count = sum(
        1 for q in questions_payload for option in q["options"] if option["state"] == "no_marcada"
    )
    ambiguous_count = sum(
        1 for q in questions_payload for option in q["options"] if option["state"] == "ambigua"
    )
    ambiguous_questions = sum(1 for q in questions_payload if len(q["ambiguous_options"]) > 0)

    if not timestamp_iso:
        timestamp_iso = datetime.now(tz=timezone.utc).isoformat()

    return {
        "template_id": metadata.get("template_id"),
        "version": metadata.get("version"),
        "timestamp": timestamp_iso,
        "quality_summary": {
            "total_questions": len(questions_payload),
            "total_options": reported_option_count,
            "marked_options": marked_count,
            "unmarked_options": unmarked_count,
            "ambiguous_options": ambiguous_count,
            "ambiguous_questions": ambiguous_questions,
        },
        "questions": questions_payload,
    }
