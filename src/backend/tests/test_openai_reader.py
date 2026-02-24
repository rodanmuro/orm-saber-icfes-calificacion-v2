from __future__ import annotations

import json

import pytest

from app.modules.omr_reader.openai_reader import (
    _map_answers_to_bubble_results,
    _parse_output,
    run_openai_omr_read,
)
from app.modules.omr_reader.openai_reader import OpenAIReadError


def _metadata() -> dict:
    return {
        "template_id": "template_basica_omr",
        "version": "v1",
        "question_items": [
            {
                "question_number": 1,
                "group_id": "G01",
                "row": 0,
                "options": [
                    {"bubble_id": "G01_00_00", "group_id": "G01", "row": 0, "col": 0, "label": "A"},
                    {"bubble_id": "G01_00_01", "group_id": "G01", "row": 0, "col": 1, "label": "B"},
                    {"bubble_id": "G01_00_02", "group_id": "G01", "row": 0, "col": 2, "label": "C"},
                    {"bubble_id": "G01_00_03", "group_id": "G01", "row": 0, "col": 3, "label": "D"},
                ],
            }
        ],
    }


def test_parse_openai_output_accepts_json_fenced() -> None:
    payload = {
        "answers": [{"question_number": 1, "marked_options": ["b"], "status": "OK"}],
        "report": {"ambiguous_questions": [], "unreadable_questions": [], "notes": "ok"},
        "notes": "ok",
    }
    text = "```json\n" + json.dumps(payload) + "\n```"
    parsed = _parse_output(text)
    assert parsed["answers"][0]["marked_options"] == ["B"]


def test_map_answers_to_bubble_results_marks_selected() -> None:
    results = _map_answers_to_bubble_results(
        metadata=_metadata(),
        answers=[{"question_number": 1, "marked_options": ["C"]}],
    )
    selected = [item for item in results if item.state == "marcada"]
    assert len(selected) == 1
    assert selected[0].label == "C"


def test_run_openai_omr_read_requires_api_key(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("app.modules.omr_reader.openai_reader.settings.openai_api_key", None)
    with pytest.raises(OpenAIReadError, match="OPENAI_API_KEY is not configured"):
        run_openai_omr_read(
            image_bytes=b"abc",
            metadata=_metadata(),
            metadata_file=tmp_path / "meta.json",
        )
