from __future__ import annotations

import pytest

from app.modules.item_ai_assistant.domain import GenerateItemDraftInput
from app.modules.item_ai_assistant.errors import ItemAIAssistantValidationError
from app.modules.item_ai_assistant.service import generate_item_draft


class _FakeProvider:
    model_name = "fake-model"

    def __init__(self, payload: dict):
        self.payload = payload

    def generate_item_draft(self, *, system_prompt: str, user_prompt: str) -> dict:
        assert "JSON" in system_prompt or "json" in system_prompt.lower()
        assert "standard_name" in user_prompt
        return self.payload


class _SequentialProvider:
    model_name = "fake-model"

    def __init__(self, payloads: list[dict]):
        self.payloads = payloads
        self.calls = 0

    def generate_item_draft(self, *, system_prompt: str, user_prompt: str) -> dict:
        idx = min(self.calls, len(self.payloads) - 1)
        self.calls += 1
        return self.payloads[idx]


def _doc_text(text: str) -> dict:
    return {
        "type": "doc",
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    }


def _doc_math(text_prefix: str, latex: str) -> dict:
    return {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": text_prefix},
                    {"type": "mathInline", "attrs": {"latex": latex}},
                ],
            }
        ],
    }


def test_generate_item_draft_structured_docs_normalizes_to_a_and_reports_cost() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_math("Calcula: ", "\\frac{1}{2}+\\frac{1}{2}"),
            "options_doc": {
                "A": _doc_text("0"),
                "B": _doc_text("1"),
                "C": _doc_text("2"),
                "D": _doc_text("3"),
            },
            "correct_answer": "b",
            "__usage": {
                "input_tokens": 1000,
                "cached_input_tokens": 200,
                "output_tokens": 300,
                "total_tokens": 1300,
            },
        }
    )
    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea una pregunta sobre fracciones",
            standard_name="Fracciones",
            competency_name="Opera fracciones",
            subject="matematicas",
            difficulty="media",
        ),
        provider=provider,
    )

    assert result.correct_answer == "A"
    assert result.options_doc["A"] == _doc_text("1")
    assert result.options_doc["B"] == _doc_text("0")
    assert result.metadata["ai_generated"] is True
    assert result.metadata["ai_model"] == "fake-model"
    assert isinstance(result.metadata["ai_prompt_version"], str)

    assert result.usage is not None
    assert result.usage["input_tokens"] == 1000
    assert result.usage["cached_input_tokens"] == 200
    assert result.usage["non_cached_input_tokens"] == 800
    assert result.usage["output_tokens"] == 300
    assert result.usage["total_tokens"] == 1300
    assert result.usage["input_cost_usd"] == pytest.approx(0.001)
    assert result.usage["cached_input_cost_usd"] == pytest.approx(0.000025)
    assert result.usage["output_cost_usd"] == pytest.approx(0.003)
    assert result.usage["total_cost_usd"] == pytest.approx(0.004025)


def test_generate_item_draft_rejects_invalid_options() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Pregunta de prueba"),
            "options_doc": {
                "A": _doc_text("1"),
                "B": _doc_text("2"),
                "C": _doc_text("3"),
            },
            "correct_answer": "A",
        }
    )

    with pytest.raises(ItemAIAssistantValidationError, match="exactly A, B, C and D"):
        generate_item_draft(
            GenerateItemDraftInput(
                user_prompt="Crea una pregunta",
                standard_name="S",
                competency_name="C",
            ),
            provider=provider,
        )


def test_generate_item_draft_accepts_valid_media_spec() -> None:
    provider = _FakeProvider(
        {
            "statement_doc": _doc_text("Interpreta el grafico"),
            "options_doc": {
                "A": _doc_text("Respuesta correcta"),
                "B": _doc_text("Distractor 1"),
                "C": _doc_text("Distractor 2"),
                "D": _doc_text("Distractor 3"),
            },
            "correct_answer": "A",
            "media_spec": {
                "mode": "chart_deterministic",
                "target": "statement",
                "spec": {
                    "chart_type": "bar",
                    "title": "Ventas",
                    "labels": ["T1", "T2"],
                    "values": [10, 12],
                },
            },
        }
    )

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con grafico de barras",
            standard_name="Datos",
            competency_name="Interpreta graficos",
        ),
        provider=provider,
    )

    assert result.media_spec is not None
    assert result.media_spec["mode"] == "chart_deterministic"
    assert result.media_spec["spec"]["chart_type"] == "bar"


def test_generate_item_draft_repair_attempt_when_first_output_is_invalid() -> None:
    invalid_first = {
        "statement_doc": _doc_text("Interpreta el grafico"),
        "options_doc": {
            "A": _doc_text("1"),
            "B": _doc_text("2"),
            "C": _doc_text("3"),
            "D": _doc_text("4"),
        },
        "correct_answer": "A",
        "media_spec": {
            "mode": "chart_deterministic",
            "target": "statement",
            "spec": {
                "chart_type": "bar",
                "labels": [],
                "values": ["abc", 20],
            },
        },
        "__usage": {
            "input_tokens": 100,
            "cached_input_tokens": 0,
            "output_tokens": 100,
            "total_tokens": 200,
        },
    }

    repaired_second = {
        "statement_doc": _doc_text("Interpreta el grafico"),
        "options_doc": {
            "A": _doc_text("1"),
            "B": _doc_text("2"),
            "C": _doc_text("3"),
            "D": _doc_text("4"),
        },
        "correct_answer": "A",
        "media_spec": {
            "mode": "chart_deterministic",
            "target": "statement",
            "spec": {
                "chart_type": "bar",
                "labels": ["T1", "T2"],
                "values": [10, 20],
            },
        },
        "__usage": {
            "input_tokens": 200,
            "cached_input_tokens": 0,
            "output_tokens": 300,
            "total_tokens": 500,
        },
    }

    provider = _SequentialProvider([invalid_first, repaired_second])

    result = generate_item_draft(
        GenerateItemDraftInput(
            user_prompt="Crea pregunta con grafico",
            standard_name="Datos",
            competency_name="Interpreta",
        ),
        provider=provider,
    )

    assert provider.calls == 2
    assert result.metadata["ai_repaired"] is True
    assert result.media_spec is not None
    assert result.usage["total_tokens"] == 700
