from __future__ import annotations

from app.modules.template_generator.metadata_validation import validate_metadata_structure


def test_validate_metadata_structure_ok() -> None:
    payload = {
        "template_id": "t",
        "version": "v1",
        "aruco_dictionary_name": "DICT_4X4_50",
        "page": {},
        "printable_area": {},
        "main_block_bbox": {},
        "block": {},
        "aruco_markers": [{}, {}, {}, {}],
        "bubbles": [{"bubble_id": "a"}, {"bubble_id": "b"}],
        "bubble_label_style": {},
        "question_numbers": [{"question_number": 1}],
        "question_number_style": {},
        "question_items": [{"question_number": 1, "options": [{"bubble_id": "a"}]}],
    }

    issues = validate_metadata_structure(payload)
    assert issues == []


def test_validate_metadata_structure_detects_errors() -> None:
    payload = {
        "template_id": "t",
        "version": "v1",
        "page": {},
        "aruco_markers": [{}, {}],
        "bubbles": [{"bubble_id": "a"}, {"bubble_id": "a"}],
        "question_items": [{"options": []}],
    }

    issues = validate_metadata_structure(payload)
    assert any("missing top-level keys" in issue for issue in issues)
    assert any("aruco_markers must contain exactly 4 elements" in issue for issue in issues)
    assert any("bubble_id values must be unique" in issue for issue in issues)
    assert any("question_items entries must contain question_number" in issue for issue in issues)
