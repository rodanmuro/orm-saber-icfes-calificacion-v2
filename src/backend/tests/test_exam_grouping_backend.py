from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.endpoints.exams import bind_item_to_exam, create_exam, publish_version, update_exam_item
from app.db.base import Base
from app.db.models import Item, Teacher
from app.schemas.exam_bank import ExamCreate, ExamItemBindRequest, ExamItemUpdateRequest, ExamVersionPublishRequest


def test_group_key_persists_and_publish_keeps_items_consecutive(tmp_path: Path) -> None:
    db_path = tmp_path / "exam_grouping_backend.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    with testing_session_local() as db:
        teacher = Teacher(
            external_uuid="teacher-grouping-001",
            email="teacher.grouping@example.com",
            first_name="Agrupacion",
            last_name="Backend",
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)

        items: list[Item] = []
        for idx, correct_answer in enumerate(["A", "B", "C", "D"], start=1):
            item = Item(
                teacher_id=teacher.id,
                statement=f"Pregunta {idx}",
                options={"A": "1", "B": "2", "C": "3", "D": "4"},
                correct_answer=correct_answer,
            )
            db.add(item)
            items.append(item)
        db.commit()
        for item in items:
            db.refresh(item)

        exam = create_exam(
            ExamCreate(
                teacher_id=teacher.id,
                exam_code="4000",
                title="Examen agrupado",
                description="Prueba de agrupacion",
            ),
            db=db,
        )

        for item in items:
            bind_item_to_exam(
                exam_id=exam.id,
                payload=ExamItemBindRequest(item_id=item.id),
                db=db,
            )

        detail = update_exam_item(
            exam_id=exam.id,
            item_id=items[1].id,
            payload=ExamItemUpdateRequest(group_key="001"),
            db=db,
        )
        detail = update_exam_item(
            exam_id=exam.id,
            item_id=items[2].id,
            payload=ExamItemUpdateRequest(group_key="1"),
            db=db,
        )

        grouped_rows = [row for row in detail.items if row.item_id in {items[1].id, items[2].id}]
        assert {row.group_key for row in grouped_rows} == {"1"}

        published = publish_version(
            exam_id=exam.id,
            payload=ExamVersionPublishRequest(
                version_code="G1",
                seed_shuffle=7,
                shuffle_questions=True,
                shuffle_options=False,
            ),
            db=db,
        )

        ordered_item_ids = [row.item_id for row in published.items]
        grouped_positions = [ordered_item_ids.index(items[1].id), ordered_item_ids.index(items[2].id)]

        assert grouped_positions[1] - grouped_positions[0] == 1
        assert grouped_positions == sorted(grouped_positions)


def test_group_key_requires_positive_integer() -> None:
    with pytest.raises(ValueError):
        ExamItemUpdateRequest(group_key="bloque-a")

    with pytest.raises(ValueError):
        ExamItemUpdateRequest(group_key="0")

    assert ExamItemUpdateRequest(group_key="001").group_key == "1"
