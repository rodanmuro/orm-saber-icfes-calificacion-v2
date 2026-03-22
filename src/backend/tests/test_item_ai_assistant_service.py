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


def test_generate_item_draft_validates_adds_metadata_normalizes_to_a_and_reports_cost() -> None:
    provider = _FakeProvider(
        {
            "statement": "Pregunta de prueba",
            "options": {"A": "Opcion A", "B": "Opcion B", "C": "Opcion C", "D": "Opcion D"},
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
            user_prompt="Crea una pregunta sobre porcentajes",
            standard_name="Porcentajes",
            competency_name="Relaciona representaciones",
            subject="matematicas",
            difficulty="media",
        ),
        provider=provider,
    )

    assert result.statement == "Pregunta de prueba"
    assert result.correct_answer == "A"
    assert result.options["A"] == "Opcion B"
    assert result.options["B"] == "Opcion A"
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
            "statement": "Pregunta de prueba",
            "options": {"A": "1", "B": "2", "C": "3"},
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
