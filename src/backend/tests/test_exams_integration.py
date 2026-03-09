from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Teacher
from app.db.session import get_db
from app.main import app


def test_exams_and_exam_items_end_to_end_http(tmp_path: Path) -> None:
    db_path = tmp_path / "exams_integration.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with testing_session_local() as db:
        teacher = Teacher(
            external_uuid="teacher-exam-001",
            email="teacher.exam@example.com",
            first_name="Docente",
            last_name="Examen",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    client = TestClient(app)
    try:
        item_payload = {
            "teacher_id": teacher_id,
            "statement": "2 + 3 = ?",
            "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
            "correct_answer": "C",
        }
        item_resp = client.post("/api/v1/items", json=item_payload)
        assert item_resp.status_code == 201
        item_id = item_resp.json()["id"]

        exam_payload = {
            "teacher_id": teacher_id,
            "exam_code": "MAT-001",
            "title": "Examen Matematicas",
            "description": "Primer parcial",
        }
        exam_resp = client.post("/api/v1/exams", json=exam_payload)
        assert exam_resp.status_code == 201
        exam_id = exam_resp.json()["id"]

        duplicate_resp = client.post("/api/v1/exams", json=exam_payload)
        assert duplicate_resp.status_code == 409

        list_resp = client.get(f"/api/v1/exams?teacher_id={teacher_id}")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

        bind_resp = client.post(f"/api/v1/exams/{exam_id}/items", json={"item_id": item_id})
        assert bind_resp.status_code == 200
        detail = bind_resp.json()
        assert len(detail["items"]) == 1
        assert detail["items"][0]["order_position"] == 1

        detail_resp = client.get(f"/api/v1/exams/{exam_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["items"][0]["item_id"] == item_id

        remove_resp = client.delete(f"/api/v1/exams/{exam_id}/items/{item_id}")
        assert remove_resp.status_code == 200
        assert remove_resp.json()["items"] == []
    finally:
        client.close()
        app.dependency_overrides.clear()

