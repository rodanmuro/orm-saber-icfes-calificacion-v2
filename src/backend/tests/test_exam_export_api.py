"""Tests automatizados para los endpoints de exportación PDF y DOCX.

Verifica que los endpoints respondan 200 y devuelvan archivos válidos
para ítems con texto plano y con ecuaciones inline (mathInline).
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Teacher
from app.db.session import get_db
from app.main import app

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _tiptap_text(text: str) -> str:
    """Doc Tiptap mínimo con un párrafo de texto plano."""
    return json.dumps({
        "type": "doc",
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
    })


def _tiptap_math_inline(before: str, latex: str, after: str) -> str:
    """Doc Tiptap con texto + mathInline + texto en un párrafo."""
    return json.dumps({
        "type": "doc",
        "content": [{
            "type": "paragraph",
            "content": [
                {"type": "text", "text": before},
                {"type": "mathInline", "attrs": {"latex": latex}},
                {"type": "text", "text": after},
            ],
        }],
    })


def _setup(tmp_path: Path):
    """Crea DB SQLite temporal, devuelve (client, teacher_id)."""
    engine = create_engine(
        f"sqlite:///{tmp_path / 'export.db'}",
        connect_args={"check_same_thread": False},
    )
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with Session() as db:
        teacher = Teacher(
            external_uuid="export-test-teacher",
            email="export@test.com",
            first_name="Export",
            last_name="Test",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    return TestClient(app), teacher_id


def _publish_version(client: TestClient, teacher_id: int, items: list[dict]) -> tuple[int, int]:
    """Crea examen con los ítems dados, publica versión, devuelve (exam_id, version_id)."""
    item_ids = []
    for item in items:
        r = client.post("/api/v1/items", json={"teacher_id": teacher_id, **item})
        assert r.status_code == 201, r.text
        item_ids.append(r.json()["id"])

    r = client.post("/api/v1/exams", json={
        "teacher_id": teacher_id,
        "exam_code": f"TEST{len(item_ids)}",
        "title": "Examen de prueba",
    })
    assert r.status_code == 201, r.text
    exam_id = r.json()["id"]

    for item_id in item_ids:
        r = client.post(f"/api/v1/exams/{exam_id}/items", json={"item_id": item_id})
        assert r.status_code == 200, r.text

    r = client.post(f"/api/v1/exams/{exam_id}/versions/publish", json={
        "version_code": "V001",
        "seed_shuffle": 0,
        "shuffle_questions": False,
        "shuffle_options": False,
    })
    assert r.status_code == 201, r.text
    return exam_id, r.json()["id"]


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def test_export_pdf_texto_plano(tmp_path: Path) -> None:
    client, teacher_id = _setup(tmp_path)
    try:
        exam_id, version_id = _publish_version(client, teacher_id, [
            {
                "statement": "¿Cuál es la capital de Colombia?",
                "options": {"A": "Cali", "B": "Bogotá", "C": "Medellín", "D": "Barranquilla"},
                "correct_answer": "B",
            },
            {
                "statement": "¿Cuánto es 2 + 2?",
                "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                "correct_answer": "B",
            },
        ])
        r = client.get(f"/api/v1/exams/{exam_id}/versions/{version_id}/export/pdf")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content.startswith(b"%PDF"), "No es un PDF válido"
        assert len(r.content) > 1_000
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_export_pdf_con_math_inline(tmp_path: Path) -> None:
    client, teacher_id = _setup(tmp_path)
    try:
        exam_id, version_id = _publish_version(client, teacher_id, [
            {
                "statement": _tiptap_math_inline("Si ", r"x^2 + 1 = 0", ", ¿cuántas soluciones reales tiene?"),
                "options": {"A": "0", "B": "1", "C": "2", "D": "Infinitas"},
                "correct_answer": "A",
            },
        ])
        r = client.get(f"/api/v1/exams/{exam_id}/versions/{version_id}/export/pdf")
        assert r.status_code == 200
        assert r.content.startswith(b"%PDF"), "No es un PDF válido"
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_export_pdf_version_inexistente(tmp_path: Path) -> None:
    client, _ = _setup(tmp_path)
    try:
        r = client.get("/api/v1/exams/99999/versions/99999/export/pdf")
        assert r.status_code == 404
    finally:
        client.close()
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

def test_export_docx_texto_plano(tmp_path: Path) -> None:
    client, teacher_id = _setup(tmp_path)
    try:
        exam_id, version_id = _publish_version(client, teacher_id, [
            {
                "statement": "¿Cuál es la raíz cuadrada de 144?",
                "options": {"A": "10", "B": "11", "C": "12", "D": "13"},
                "correct_answer": "C",
            },
        ])
        r = client.get(f"/api/v1/exams/{exam_id}/versions/{version_id}/export/docx")
        assert r.status_code == 200
        assert DOCX_MIME in r.headers["content-type"]
        assert r.content.startswith(b"PK"), "No es un DOCX/ZIP válido"
        assert len(r.content) > 1_000
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_export_docx_con_math_inline(tmp_path: Path) -> None:
    client, teacher_id = _setup(tmp_path)
    try:
        exam_id, version_id = _publish_version(client, teacher_id, [
            {
                "statement": _tiptap_math_inline(
                    "El valor de ", r"\frac{a}{b} + \frac{b}{a}", " cuando a=b es:"
                ),
                "options": {
                    "A": _tiptap_text("1"),
                    "B": _tiptap_text("2"),
                    "C": _tiptap_text("0"),
                    "D": _tiptap_text("Indefinido"),
                },
                "correct_answer": "B",
            },
        ])
        r = client.get(f"/api/v1/exams/{exam_id}/versions/{version_id}/export/docx")
        assert r.status_code == 200
        assert r.content.startswith(b"PK"), "No es un DOCX/ZIP válido"
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_export_docx_version_inexistente(tmp_path: Path) -> None:
    client, _ = _setup(tmp_path)
    try:
        r = client.get("/api/v1/exams/99999/versions/99999/export/docx")
        assert r.status_code == 404
    finally:
        client.close()
        app.dependency_overrides.clear()
