from __future__ import annotations

import pytest

from app.modules.omr_reader.contracts import BubbleReadResult
from app.modules.omr_reader.errors import BubbleReadError
from app.modules.omr_reader.result_builder import build_omr_read_result


def _metadata_question_items() -> dict:
    return {
        "template_id": "template_test",
        "version": "v1",
        "question_items": [
            {
                "group_id": "G01",
                "row": 0,
                "question_number": 1,
                "options": [
                    {"bubble_id": "G01_00_00", "label": "A"},
                    {"bubble_id": "G01_00_01", "label": "B"},
                ],
            },
            {
                "group_id": "G01",
                "row": 1,
                "question_number": 2,
                "options": [
                    {"bubble_id": "G01_01_00", "label": "A"},
                    {"bubble_id": "G01_01_01", "label": "B"},
                ],
            },
        ],
    }


def _bubble_results() -> list[BubbleReadResult]:
    return [
        BubbleReadResult(
            bubble_id="G01_00_00",
            group_id="G01",
            row=0,
            col=0,
            label="A",
            fill_ratio=0.62,
            state="marcada",
        ),
        BubbleReadResult(
            bubble_id="G01_00_01",
            group_id="G01",
            row=0,
            col=1,
            label="B",
            fill_ratio=0.02,
            state="no_marcada",
        ),
        BubbleReadResult(
            bubble_id="G01_01_00",
            group_id="G01",
            row=1,
            col=0,
            label="A",
            fill_ratio=0.40,
            state="ambigua",
        ),
        BubbleReadResult(
            bubble_id="G01_01_01",
            group_id="G01",
            row=1,
            col=1,
            label="B",
            fill_ratio=0.01,
            state="no_marcada",
        ),
    ]


def test_build_omr_read_result_success() -> None:
    payload = build_omr_read_result(
        metadata=_metadata_question_items(),
        bubble_results=_bubble_results(),
        timestamp_iso="2026-02-23T00:00:00+00:00",
    )

    assert payload["template_id"] == "template_test"
    assert payload["version"] == "v1"
    assert payload["quality_summary"]["total_questions"] == 2
    assert payload["quality_summary"]["total_options"] == 4
    assert payload["quality_summary"]["marked_options"] == 1
    assert payload["quality_summary"]["ambiguous_options"] == 1
    assert payload["quality_summary"]["ambiguous_questions"] == 1

    q1 = payload["questions"][0]
    assert q1["question_number"] == 1
    assert q1["marked_options"] == ["A"]
    assert q1["ambiguous_options"] == []

    q2 = payload["questions"][1]
    assert q2["question_number"] == 2
    assert q2["marked_options"] == []
    assert q2["ambiguous_options"] == ["A"]


def test_build_omr_read_result_fails_when_missing_option_result() -> None:
    results = _bubble_results()[:-1]
    with pytest.raises(BubbleReadError, match="missing bubble result"):
        build_omr_read_result(metadata=_metadata_question_items(), bubble_results=results)


def test_build_omr_read_result_fails_with_extra_result() -> None:
    results = _bubble_results() + [
        BubbleReadResult(
            bubble_id="EXTRA_01",
            group_id="G99",
            row=0,
            col=0,
            label="X",
            fill_ratio=0.5,
            state="marcada",
        )
    ]
    with pytest.raises(BubbleReadError, match="not present in metadata question_items"):
        build_omr_read_result(metadata=_metadata_question_items(), bubble_results=results)


def test_build_omr_read_result_resolves_multiple_marked_by_highest_ratio() -> None:
    results = [
        BubbleReadResult(
            bubble_id="G01_00_00",
            group_id="G01",
            row=0,
            col=0,
            label="A",
            fill_ratio=0.31,
            state="marcada",
        ),
        BubbleReadResult(
            bubble_id="G01_00_01",
            group_id="G01",
            row=0,
            col=1,
            label="B",
            fill_ratio=0.42,
            state="marcada",
        ),
        BubbleReadResult(
            bubble_id="G01_01_00",
            group_id="G01",
            row=1,
            col=0,
            label="A",
            fill_ratio=0.0,
            state="no_marcada",
        ),
        BubbleReadResult(
            bubble_id="G01_01_01",
            group_id="G01",
            row=1,
            col=1,
            label="B",
            fill_ratio=0.0,
            state="no_marcada",
        ),
    ]

    payload = build_omr_read_result(metadata=_metadata_question_items(), bubble_results=results)
    q1 = payload["questions"][0]

    assert q1["marked_options"] == ["B"]
    assert "A" in q1["ambiguous_options"]

    by_label = {item["label"]: item for item in q1["options"]}
    assert by_label["B"]["state"] == "marcada"
    assert by_label["A"]["state"] == "ambigua"
