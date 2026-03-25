from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.modules.item_ai_assistant.domain import GenerateItemDraftOutput


def _doc_text(text: str) -> dict:
    return {
        "type": "doc",
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    }


def test_generate_item_endpoint_ok(monkeypatch) -> None:
    def _fake_generate_item_draft(_payload):
        return GenerateItemDraftOutput(
            statement_doc=_doc_text("Enunciado generado"),
            options_doc={"A": _doc_text("1"), "B": _doc_text("2"), "C": _doc_text("3"), "D": _doc_text("4")},
            correct_answer="C",
            metadata={
                "ai_generated": True,
                "ai_model": "fake-model",
                "ai_prompt_version": "v1",
            },
            usage={
                "model": "fake-model",
                "input_tokens": 10,
                "cached_input_tokens": 0,
                "non_cached_input_tokens": 10,
                "output_tokens": 20,
                "total_tokens": 30,
                "input_cost_usd": 0.0,
                "cached_input_cost_usd": 0.0,
                "output_cost_usd": 0.0,
                "total_cost_usd": 0.0,
                "pricing_input_per_1m_usd": 1.25,
                "pricing_cached_input_per_1m_usd": 0.125,
                "pricing_output_per_1m_usd": 10.0,
            },
            media_spec={
                "mode": "chart_deterministic",
                "target": "statement",
                "spec": {"chart_type": "bar", "labels": ["A", "B"], "values": [1, 2]},
            },
            media_specs=[
                {
                    "mode": "chart_deterministic",
                    "target": "statement",
                    "spec": {"chart_type": "bar", "labels": ["A", "B"], "values": [1, 2]},
                }
            ],
        )

    monkeypatch.setattr(
        "app.api.v1.endpoints.ai_assistant.generate_item_draft",
        _fake_generate_item_draft,
    )

    payload = {
        "user_prompt": "Genera pregunta de porcentajes",
        "standard_name": "Porcentajes",
        "competency_name": "Interpreta representaciones",
        "subject": "matematicas",
        "difficulty": "media",
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/ai/generate-item", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["statement_doc"]["type"] == "doc"
    assert body["correct_answer"] == "C"
    assert body["options_doc"].keys() == {"A", "B", "C", "D"}
    assert body["metadata"]["ai_generated"] is True
    assert body["usage"]["input_tokens"] == 10
    assert body["media_spec"]["mode"] == "chart_deterministic"
    assert len(body["media_specs"]) == 1


def test_generate_item_endpoint_blocks_missing_curriculum_context() -> None:
    payload = {
        "user_prompt": "Genera pregunta",
        "standard_name": "",
        "competency_name": "",
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/ai/generate-item", json=payload)

    assert response.status_code == 422
