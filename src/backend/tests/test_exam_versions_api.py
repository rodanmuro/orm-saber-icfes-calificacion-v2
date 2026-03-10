from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import Teacher
from app.db.session import get_db
from app.main import app


def test_publish_exam_version_from_exam_items(tmp_path: Path) -> None:
    db_path = tmp_path / "exam_versions_api.db"
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
            external_uuid="teacher-version-001",
            email="teacher.version@example.com",
            first_name="Version",
            last_name="Teacher",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    client = TestClient(app)
    try:
        item_payloads = [
            {
                "teacher_id": teacher_id,
                "statement": "Pregunta 1",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_answer": "A",
            },
            {
                "teacher_id": teacher_id,
                "statement": "Pregunta 2",
                "options": {"A": "a", "B": "b", "C": "c", "D": "d"},
                "correct_answer": "C",
            },
        ]
        item_ids: list[int] = []
        for payload in item_payloads:
            response = client.post("/api/v1/items", json=payload)
            assert response.status_code == 201
            item_ids.append(response.json()["id"])

        exam_response = client.post(
            "/api/v1/exams",
            json={
                "teacher_id": teacher_id,
                "exam_code": "1234",
                "title": "Demo Exam",
                "description": "Exam de prueba",
            },
        )
        assert exam_response.status_code == 201
        exam_id = exam_response.json()["id"]

        for item_id in item_ids:
            bind_response = client.post(
                f"/api/v1/exams/{exam_id}/items",
                json={"item_id": item_id},
            )
            assert bind_response.status_code == 200

        publish_response = client.post(
            f"/api/v1/exams/{exam_id}/versions/publish",
            json={
                "version_code": "V001",
                "seed_shuffle": 42,
                "shuffle_questions": True,
                "shuffle_options": True,
            },
        )
        assert publish_response.status_code == 201
        published = publish_response.json()
        assert published["version_code"] == "V001"
        assert published["seed_shuffle"] == 42
        assert len(published["items"]) == 2
        assert set(published["answer_key"].keys()) == {"1", "2"}

        versions_response = client.get(f"/api/v1/exams/{exam_id}/versions")
        assert versions_response.status_code == 200
        versions = versions_response.json()
        assert len(versions) == 1

        version_id = versions[0]["id"]
        version_detail_response = client.get(f"/api/v1/exams/{exam_id}/versions/{version_id}")
        assert version_detail_response.status_code == 200
        detail = version_detail_response.json()
        assert detail["id"] == version_id
        assert len(detail["items"]) == 2
    finally:
        client.close()
        app.dependency_overrides.clear()
