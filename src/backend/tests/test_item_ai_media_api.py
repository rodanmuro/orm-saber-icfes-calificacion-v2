from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import app.modules.item_ai_assistant.media_service as media_service
from app.main import app


def test_generate_media_bar_chart_creates_asset(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(media_service, "ASSETS_DIR", tmp_path)

    client = TestClient(app)
    response = client.post(
        "/api/v1/ai/generate-media",
        json={
            "teacher_id": 1,
            "mode": "chart_deterministic",
            "target": "statement",
            "spec": {
                "chart_type": "bar",
                "title": "Ventas",
                "x_label": "Mes",
                "y_label": "Valor",
                "labels": ["Ene", "Feb", "Mar"],
                "values": [10, 15, 8],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    filename = payload["asset"]["filename"]
    assert filename.endswith(".png")
    assert (tmp_path / filename).exists()
    assert payload["insert_doc"]["content"][0]["type"] == "image"


def test_generate_media_rejects_unknown_chart_type() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/ai/generate-media",
        json={
            "teacher_id": 1,
            "mode": "chart_deterministic",
            "target": "statement",
            "spec": {
                "chart_type": "radar",
                "labels": ["A", "B"],
                "values": [1, 2],
            },
        },
    )

    assert response.status_code == 422
    assert "chart_type" in response.json()["detail"]


def test_generate_media_bar_chart_accepts_numeric_strings(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(media_service, "ASSETS_DIR", tmp_path)

    client = TestClient(app)
    response = client.post(
        "/api/v1/ai/generate-media",
        json={
            "teacher_id": 1,
            "mode": "chart_deterministic",
            "target": "statement",
            "spec": {
                "chart_type": "bar",
                "title": "Transporte",
                "labels": ["Bus", "Bicicleta", "Caminando", "Carro"],
                "values": ["12", "8", "10", "10"],
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert (tmp_path / payload["asset"]["filename"]).exists()
