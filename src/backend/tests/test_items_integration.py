from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Teacher
from app.db.session import get_db
from app.main import app


def test_items_end_to_end_http(tmp_path: Path) -> None:
    db_path = tmp_path / "items_integration.db"
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
            external_uuid="teacher-integration-001",
            email="teacher.integration@example.com",
            first_name="Docente",
            last_name="Integracion",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    client = TestClient(app)
    try:
        create_payload = {
            "teacher_id": teacher_id,
            "statement": "La capital de Colombia es:",
            "options": {"A": "Bogota", "B": "Medellin", "C": "Cali", "D": "Cartagena"},
            "correct_answer": "A",
            "subject": "sociales",
            "difficulty": "media",
            "curriculum": {
                "standard_code": "STD-SOC-001",
                "standard_name": "Ubicacion geografica",
                "competency_code": "COMP-SOC-001",
                "competency_name": "Identificacion territorial",
            },
        }
        create_response = client.post("/api/v1/items", json=create_payload)
        assert create_response.status_code == 201
        created = create_response.json()
        item_id = created["id"]
        assert created["correct_answer"] == "A"
        assert created["curriculum"]["standard_code"] == "STD-SOC-001"

        list_response = client.get("/api/v1/items")
        assert list_response.status_code == 200
        listed = list_response.json()
        assert len(listed) == 1
        assert listed[0]["id"] == item_id

        get_response = client.get(f"/api/v1/items/{item_id}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["statement"] == "La capital de Colombia es:"

        invalid_payload = {
            "teacher_id": teacher_id,
            "statement": "Pregunta invalida",
            "options": {"A": "A", "B": "B", "C": "C"},
            "correct_answer": "A",
        }
        invalid_response = client.post("/api/v1/items", json=invalid_payload)
        assert invalid_response.status_code == 422
    finally:
        client.close()
        app.dependency_overrides.clear()

