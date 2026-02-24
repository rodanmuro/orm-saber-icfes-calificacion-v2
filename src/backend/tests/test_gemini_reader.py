from __future__ import annotations

import json

import pytest

from app.modules.omr_reader.errors import GeminiReadError
from app.modules.omr_reader.gemini_reader import (
    _extract_gemini_usage,
    _map_answers_to_bubble_results,
    _parse_gemini_output,
    ping_gemini_model,
    run_gemini_omr_read,
)


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


def test_parse_gemini_output_accepts_json_fenced() -> None:
    payload = {
        "answers": [{"question_number": 1, "marked_options": ["b"], "status": "OK"}],
        "report": {"ambiguous_questions": [], "unreadable_questions": [], "notes": "ok"},
        "notes": "ok",
    }
    text = "```json\n" + json.dumps(payload) + "\n```"
    parsed = _parse_gemini_output(text)
    assert parsed["answers"][0]["question_number"] == 1
    assert parsed["answers"][0]["marked_options"] == ["B"]
    assert parsed["report"]["ambiguous_questions"] == []


def test_parse_gemini_output_rejects_invalid_json() -> None:
    with pytest.raises(GeminiReadError, match="not valid JSON"):
        _parse_gemini_output("no-es-json")


def test_map_answers_to_bubble_results_marks_selected() -> None:
    results = _map_answers_to_bubble_results(
        metadata=_metadata(),
        answers=[{"question_number": 1, "marked_options": ["C"]}],
    )
    selected = [item for item in results if item.state == "marcada"]
    assert len(selected) == 1
    assert selected[0].label == "C"
    assert selected[0].fill_ratio == 1.0


def test_parse_gemini_output_merges_report_and_status_revisar() -> None:
    payload = {
        "answers": [
            {"question_number": 2, "marked_options": ["A", "B"], "status": "REVISAR"},
            {"question_number": 3, "marked_options": [], "status": "REVISAR"},
        ],
        "report": {
            "ambiguous_questions": [5],
            "unreadable_questions": ["7"],
            "notes": "rev",
        },
    }
    parsed = _parse_gemini_output(json.dumps(payload))
    assert parsed["report"]["ambiguous_questions"] == [2, 5]
    assert parsed["report"]["unreadable_questions"] == [3, 7]


def test_run_gemini_omr_read_requires_api_key(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("app.modules.omr_reader.gemini_reader.settings.gemini_api_key", None)
    with pytest.raises(GeminiReadError, match="GEMINI_API_KEY is not configured"):
        run_gemini_omr_read(
            image_bytes=b"abc",
            metadata=_metadata(),
            metadata_file=tmp_path / "meta.json",
        )


def test_ping_gemini_model_requires_api_key(monkeypatch) -> None:
    monkeypatch.setattr("app.modules.omr_reader.gemini_reader.settings.gemini_api_key", None)
    with pytest.raises(GeminiReadError, match="GEMINI_API_KEY is not configured"):
        ping_gemini_model()


def test_extract_gemini_usage_from_usage_metadata_namespace() -> None:
    class Usage:
        prompt_token_count = 123
        candidates_token_count = 45
        total_token_count = 168
        thoughts_token_count = None
        cached_content_token_count = 0

    class Response:
        usage_metadata = Usage()

    usage = _extract_gemini_usage(Response())
    assert usage["prompt_token_count"] == 123
    assert usage["candidates_token_count"] == 45
    assert usage["total_token_count"] == 168
    assert usage["cached_content_token_count"] == 0
