from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import OmrAttempt, Teacher
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

        pdf_response = client.get(f"/api/v1/exams/{exam_id}/versions/{version_id}/export/pdf")
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"
        assert "attachment; filename=" in pdf_response.headers.get("content-disposition", "")
        assert pdf_response.content.startswith(b"%PDF")
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_reorder_exam_version_updates_question_numbers_and_answer_key(tmp_path: Path) -> None:
    db_path = tmp_path / "exam_versions_reorder_api.db"
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
            external_uuid="teacher-version-002",
            email="teacher.version2@example.com",
            first_name="Version2",
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
            {
                "teacher_id": teacher_id,
                "statement": "Pregunta 3",
                "options": {"A": "x", "B": "y", "C": "z", "D": "w"},
                "correct_answer": "B",
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
                "exam_code": "2000",
                "title": "Demo Reorder",
                "description": "Exam de prueba reorder",
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
                "version_code": "1",
                "seed_shuffle": 99,
                "shuffle_questions": True,
                "shuffle_options": True,
            },
        )
        assert publish_response.status_code == 201
        published = publish_response.json()
        version_id = published["id"]
        original_items = published["items"]
        assert len(original_items) == 3
        assert all("id" in row for row in original_items)

        reversed_ids = [row["id"] for row in reversed(original_items)]
        reorder_response = client.patch(
            f"/api/v1/exams/{exam_id}/versions/{version_id}/reorder",
            json={"ordered_version_item_ids": reversed_ids},
        )
        assert reorder_response.status_code == 200
        reordered = reorder_response.json()

        reordered_items = reordered["items"]
        assert [row["id"] for row in reordered_items] == reversed_ids
        assert [row["question_number"] for row in reordered_items] == [1, 2, 3]

        expected_key = {
            str(index): row["correct_answer_mapped"]
            for index, row in enumerate(reordered_items, start=1)
        }
        assert reordered["answer_key"] == expected_key

        detail_response = client.get(f"/api/v1/exams/{exam_id}/versions/{version_id}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["answer_key"] == expected_key
        assert [row["id"] for row in detail["items"]] == reversed_ids
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_publish_exam_version_keeps_grouped_exam_items_together(tmp_path: Path) -> None:
    db_path = tmp_path / "exam_versions_grouped_api.db"
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
            external_uuid="teacher-version-003",
            email="teacher.version3@example.com",
            first_name="Version3",
            last_name="Teacher",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    client = TestClient(app)
    try:
        item_ids: list[int] = []
        for idx, correct_answer in enumerate(["A", "B", "C", "D"], start=1):
            response = client.post(
                "/api/v1/items",
                json={
                    "teacher_id": teacher_id,
                    "statement": f"Pregunta {idx}",
                    "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                    "correct_answer": correct_answer,
                },
            )
            assert response.status_code == 201
            item_ids.append(response.json()["id"])

        exam_response = client.post(
            "/api/v1/exams",
            json={
                "teacher_id": teacher_id,
                "exam_code": "3000",
                "title": "Demo Grouped",
                "description": "Exam de prueba grouped",
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

        patch_one = client.patch(
            f"/api/v1/exams/{exam_id}/items/{item_ids[1]}",
            json={"group_key": "001"},
        )
        assert patch_one.status_code == 200
        patch_two = client.patch(
            f"/api/v1/exams/{exam_id}/items/{item_ids[2]}",
            json={"group_key": "1"},
        )
        assert patch_two.status_code == 200
        exam_detail = patch_two.json()
        grouped_rows = [row for row in exam_detail["items"] if row["item_id"] in {item_ids[1], item_ids[2]}]
        assert {row["group_key"] for row in grouped_rows} == {"1"}

        publish_response = client.post(
            f"/api/v1/exams/{exam_id}/versions/publish",
            json={
                "version_code": "G1",
                "seed_shuffle": 7,
                "shuffle_questions": True,
                "shuffle_options": False,
            },
        )
        assert publish_response.status_code == 201
        published = publish_response.json()
        ordered_item_ids = [row["item_id"] for row in published["items"]]
        grouped_positions = [ordered_item_ids.index(item_ids[1]), ordered_item_ids.index(item_ids[2])]

        assert grouped_positions[1] - grouped_positions[0] == 1
        assert grouped_positions == sorted(grouped_positions)
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_delete_exam_version_without_linked_attempts(tmp_path: Path) -> None:
    db_path = tmp_path / "exam_versions_delete_api.db"
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
            external_uuid="teacher-version-004",
            email="teacher.version4@example.com",
            first_name="Version4",
            last_name="Teacher",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    client = TestClient(app)
    try:
        item_response = client.post(
            "/api/v1/items",
            json={
                "teacher_id": teacher_id,
                "statement": "Pregunta delete",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_answer": "A",
            },
        )
        assert item_response.status_code == 201
        item_id = item_response.json()["id"]

        exam_response = client.post(
            "/api/v1/exams",
            json={
                "teacher_id": teacher_id,
                "exam_code": "4001",
                "title": "Demo Delete",
                "description": "Exam delete",
            },
        )
        assert exam_response.status_code == 201
        exam_id = exam_response.json()["id"]

        bind_response = client.post(f"/api/v1/exams/{exam_id}/items", json={"item_id": item_id})
        assert bind_response.status_code == 200

        publish_response = client.post(
            f"/api/v1/exams/{exam_id}/versions/publish",
            json={
                "version_code": "1",
                "seed_shuffle": 11,
                "shuffle_questions": True,
                "shuffle_options": True,
            },
        )
        assert publish_response.status_code == 201
        version_id = publish_response.json()["id"]

        delete_response = client.delete(f"/api/v1/exams/{exam_id}/versions/{version_id}")
        assert delete_response.status_code == 200
        assert delete_response.json() == {"deleted": True, "version_id": version_id}

        versions_response = client.get(f"/api/v1/exams/{exam_id}/versions")
        assert versions_response.status_code == 200
        assert versions_response.json() == []
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_delete_exam_version_fails_with_linked_omr_attempts(tmp_path: Path) -> None:
    db_path = tmp_path / "exam_versions_delete_blocked_api.db"
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
            external_uuid="teacher-version-005",
            email="teacher.version5@example.com",
            first_name="Version5",
            last_name="Teacher",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        teacher_id = teacher.id

    client = TestClient(app)
    try:
        item_response = client.post(
            "/api/v1/items",
            json={
                "teacher_id": teacher_id,
                "statement": "Pregunta delete blocked",
                "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                "correct_answer": "A",
            },
        )
        assert item_response.status_code == 201
        item_id = item_response.json()["id"]

        exam_response = client.post(
            "/api/v1/exams",
            json={
                "teacher_id": teacher_id,
                "exam_code": "4002",
                "title": "Demo Delete Blocked",
                "description": "Exam delete blocked",
            },
        )
        assert exam_response.status_code == 201
        exam_id = exam_response.json()["id"]

        bind_response = client.post(f"/api/v1/exams/{exam_id}/items", json={"item_id": item_id})
        assert bind_response.status_code == 200

        publish_response = client.post(
            f"/api/v1/exams/{exam_id}/versions/publish",
            json={
                "version_code": "1",
                "seed_shuffle": 12,
                "shuffle_questions": True,
                "shuffle_options": True,
            },
        )
        assert publish_response.status_code == 201
        version_id = publish_response.json()["id"]

        with testing_session_local() as db:
            attempt = OmrAttempt(
                teacher_id=teacher_id,
                exam_id=exam_id,
                exam_version_id=version_id,
                status="graded",
                total_questions=1,
                correct_count=1,
                incorrect_count=0,
                blank_count=0,
                ambiguous_count=0,
                manual_review_required=False,
            )
            db.add(attempt)
            db.commit()

        delete_response = client.delete(f"/api/v1/exams/{exam_id}/versions/{version_id}")
        assert delete_response.status_code == 409
        assert delete_response.json()["detail"] == "cannot delete exam version with linked omr attempts"
    finally:
        client.close()
        app.dependency_overrides.clear()
