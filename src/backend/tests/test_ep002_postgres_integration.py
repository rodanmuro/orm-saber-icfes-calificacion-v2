from __future__ import annotations

import os

from fastapi.testclient import TestClient
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from app.db.models import Exam, ExamItem, ExamVersion, ExamVersionItem, Item, Teacher
from app.db.session import SessionLocal
from app.main import app


def _cleanup_teacher_scope(db: Session, teacher_email: str) -> None:
    teacher = db.scalar(select(Teacher).where(Teacher.email == teacher_email))
    if teacher is None:
        return

    exams = db.scalars(select(Exam).where(Exam.teacher_id == teacher.id)).all()
    exam_ids = [exam.id for exam in exams]

    if exam_ids:
        version_ids = db.scalars(
            select(ExamVersion.id).where(ExamVersion.exam_id.in_(exam_ids))
        ).all()
        if version_ids:
            db.execute(
                delete(ExamVersionItem).where(ExamVersionItem.exam_version_id.in_(version_ids))
            )
            db.execute(delete(ExamVersion).where(ExamVersion.id.in_(version_ids)))

        db.execute(delete(ExamItem).where(ExamItem.exam_id.in_(exam_ids)))
        db.execute(delete(Exam).where(Exam.id.in_(exam_ids)))

    db.execute(delete(Item).where(Item.teacher_id == teacher.id))

    db.delete(teacher)
    db.commit()


def test_ep002_end_to_end_on_postgres() -> None:
    database_url = os.getenv("DATABASE_URL", "")
    assert database_url.startswith("postgresql+psycopg://"), (
        "Este test debe ejecutarse con DATABASE_URL apuntando a PostgreSQL"
    )

    teacher_email = "teacher.ep002.pg@example.com"

    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
        _cleanup_teacher_scope(db=db, teacher_email=teacher_email)

        teacher = Teacher(
            external_uuid="teacher-ep002-pg-001",
            email=teacher_email,
            first_name="Teacher",
            last_name="Postgres",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    client = TestClient(app)
    try:
        payloads = [
            {
                "teacher_id": teacher_id,
                "statement": "Pregunta PG 1",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_answer": "A",
                "subject": "matematicas",
                "difficulty": "baja",
            },
            {
                "teacher_id": teacher_id,
                "statement": "Pregunta PG 2",
                "options": {"A": "a", "B": "b", "C": "c", "D": "d"},
                "correct_answer": "C",
                "subject": "lenguaje",
                "difficulty": "media",
            },
        ]

        item_ids: list[int] = []
        for payload in payloads:
            created = client.post("/api/v1/items", json=payload)
            assert created.status_code == 201
            item_ids.append(created.json()["id"])

        listed_items = client.get("/api/v1/items")
        assert listed_items.status_code == 200
        assert any(i["id"] == item_ids[0] for i in listed_items.json())

        exam_created = client.post(
            "/api/v1/exams",
            json={
                "teacher_id": teacher_id,
                "exam_code": "PG1001",
                "title": "Examen PG EP002",
                "description": "Integracion EP_002 en PostgreSQL",
            },
        )
        assert exam_created.status_code == 201
        exam_id = exam_created.json()["id"]

        for item_id in item_ids:
            bind_resp = client.post(
                f"/api/v1/exams/{exam_id}/items",
                json={"item_id": item_id},
            )
            assert bind_resp.status_code == 200

        published = client.post(
            f"/api/v1/exams/{exam_id}/versions/publish",
            json={
                "version_code": "V001",
                "seed_shuffle": 20260311,
                "shuffle_questions": True,
                "shuffle_options": True,
            },
        )
        assert published.status_code == 201
        body = published.json()
        assert body["version_code"] == "V001"
        assert len(body["items"]) == 2
        assert set(body["answer_key"].keys()) == {"1", "2"}

        versions = client.get(f"/api/v1/exams/{exam_id}/versions")
        assert versions.status_code == 200
        assert len(versions.json()) == 1

        answer_key = client.get(f"/api/v1/exams/{exam_id}/answer-key")
        assert answer_key.status_code == 200
        answer_key_json = answer_key.json()["answer_key"]
        assert isinstance(answer_key_json, list)
        assert len(answer_key_json) == 2

        # Contrato actual: lista estructurada por pregunta/version.
        by_question = {str(row["question_number"]): row["correct_answer"] for row in answer_key_json}
        assert by_question == {"1": "A", "2": "C"}

        for row in answer_key_json:
            assert set(row.keys()) >= {
                "question_number",
                "order_position",
                "item_id",
                "correct_answer",
            }
    finally:
        client.close()
        with SessionLocal() as db:
            _cleanup_teacher_scope(db=db, teacher_email=teacher_email)
