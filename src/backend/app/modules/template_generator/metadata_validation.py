from __future__ import annotations

from typing import Any

REQUIRED_TOP_LEVEL_KEYS = {
    "template_id",
    "version",
    "aruco_dictionary_name",
    "page",
    "printable_area",
    "main_block_bbox",
    "block",
    "aruco_markers",
    "bubbles",
    "bubble_label_style",
    "question_numbers",
    "question_number_style",
    "question_items",
}


def validate_metadata_structure(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    missing = REQUIRED_TOP_LEVEL_KEYS - set(payload.keys())
    if missing:
        issues.append(f"missing top-level keys: {sorted(missing)}")

    markers = payload.get("aruco_markers", [])
    if not isinstance(markers, list) or len(markers) != 4:
        issues.append("aruco_markers must contain exactly 4 elements")

    bubbles = payload.get("bubbles", [])
    if not isinstance(bubbles, list) or len(bubbles) == 0:
        issues.append("bubbles must be a non-empty list")
    else:
        bubble_ids = [item.get("bubble_id") for item in bubbles if isinstance(item, dict)]
        if len(set(bubble_ids)) != len(bubble_ids):
            issues.append("bubble_id values must be unique")

    question_items = payload.get("question_items", [])
    if not isinstance(question_items, list) or len(question_items) == 0:
        issues.append("question_items must be a non-empty list")
    else:
        for item in question_items:
            if not isinstance(item, dict):
                issues.append("question_items entries must be objects")
                continue
            if "question_number" not in item:
                issues.append("question_items entries must contain question_number")
            options = item.get("options", [])
            if not isinstance(options, list) or len(options) == 0:
                issues.append("question_items entries must contain non-empty options")

    return issues
