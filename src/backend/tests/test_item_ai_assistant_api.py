from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.modules.item_ai_assistant.domain import GenerateItemDraftOutput


def test_generate_item_endpoint_ok(monkeypatch) -> None:
    def _fake_generate_item_draft(_payload):
        return GenerateItemDraftOutput(
            statement="Enunciado generado",
            options={"A": "1", "B": "2", "C": "3", "D": "4"},
            correct_answer="C",
            metadata={
                "ai_generated": True,
                "ai_model": "fake-model",
                "ai_prompt_version": "v1",
            },
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
    assert body["statement"] == "Enunciado generado"
    assert body["correct_answer"] == "C"
    assert body["options"].keys() == {"A", "B", "C", "D"}
    assert body["metadata"]["ai_generated"] is True


def test_generate_item_endpoint_blocks_missing_curriculum_context() -> None:
    payload = {
        "user_prompt": "Genera pregunta",
        "standard_name": "",
        "competency_name": "",
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/ai/generate-item", json=payload)

    assert response.status_code == 422
