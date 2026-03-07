from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models import Teacher
from app.db.session import get_db
from app.main import app


def _build_test_db(tmp_path: Path) -> sessionmaker:
    db_path = tmp_path / "items_api_test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestingSessionLocal


def test_create_and_get_item(tmp_path: Path) -> None:
    SessionLocal = _build_test_db(tmp_path)
    with SessionLocal() as db:
        teacher = Teacher(
            external_uuid="teacher-001",
            email="teacher1@example.com",
            first_name="Ada",
            last_name="Lovelace",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    payload = {
        "teacher_id": teacher_id,
        "statement": "2 + 2 es igual a:",
        "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
        "correct_answer": "B",
        "subject": "matematicas",
        "difficulty": "baja",
        "curriculum": {
            "standard_code": "STD-MAT-001",
            "standard_name": "Operaciones basicas",
            "competency_code": "COMP-MAT-001",
            "competency_name": "Resolucion de problemas",
        },
    }
    with TestClient(app) as client:
        created = client.post("/api/v1/items", json=payload)
        assert created.status_code == 201
        body = created.json()
        assert body["correct_answer"] == "B"
        assert body["options"]["B"] == "4"
        assert body["curriculum"]["standard_code"] == "STD-MAT-001"

        fetched = client.get(f"/api/v1/items/{body['id']}")
        assert fetched.status_code == 200
        fetched_body = fetched.json()
        assert fetched_body["id"] == body["id"]
        assert fetched_body["teacher_id"] == teacher_id

        listed = client.get("/api/v1/items")
        assert listed.status_code == 200
        assert len(listed.json()) == 1

    app.dependency_overrides.clear()


def test_reject_item_with_incomplete_options(tmp_path: Path) -> None:
    SessionLocal = _build_test_db(tmp_path)
    with SessionLocal() as db:
        teacher = Teacher(
            external_uuid="teacher-002",
            email="teacher2@example.com",
            first_name="Grace",
            last_name="Hopper",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    payload = {
        "teacher_id": teacher_id,
        "statement": "Capital de Francia:",
        "options": {"A": "Paris", "B": "Madrid", "C": "Roma"},
        "correct_answer": "A",
    }
    with TestClient(app) as client:
        response = client.post("/api/v1/items", json=payload)
        assert response.status_code == 422

    app.dependency_overrides.clear()
