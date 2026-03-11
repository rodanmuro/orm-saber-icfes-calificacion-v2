from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.init_db import init_db
from app.db.models import (
    Exam,
    ExamItem,
    ExamVersion,
    ExamVersionItem,
    Item,
    OmrAttempt,
    Teacher,
)
from app.db.session import SessionLocal
from app.modules.exam_version.service import publish_exam_version

SEED_BATCH = "dummy_exam_40_v1"
TEACHER_EMAIL = "docente.dummy40@omr.local"
EXAM_CODE = "1234"
TOTAL_QUESTIONS = 40
SUBJECT = "dummy"
DIFFICULTY = "baja"

VERSION_CODE = "V001"
VERSION_SEED = 424242


def option_set(n: int) -> dict[str, str]:
    return {
        "A": f"Opcion A de la pregunta {n}",
        "B": f"Opcion B de la pregunta {n}",
        "C": f"Opcion C de la pregunta {n}",
        "D": f"Opcion D de la pregunta {n}",
    }


def correct_answer_for(n: int) -> str:
    return ["A", "B", "C", "D"][(n - 1) % 4]


def _delete_existing_dataset(db, teacher: Teacher) -> None:
    exam = db.scalar(select(Exam).where(Exam.teacher_id == teacher.id, Exam.exam_code == EXAM_CODE))
    if exam is not None:
        db.delete(exam)
        db.flush()

    old_items = db.scalars(
        select(Item).where(
            Item.teacher_id == teacher.id,
            Item.subject == SUBJECT,
            Item.metadata_json["seed_batch"].as_string() == SEED_BATCH,
        )
    ).all()
    for old_item in old_items:
        db.delete(old_item)
    db.flush()

    stale_attempts = db.scalars(
        select(OmrAttempt).where(
            OmrAttempt.teacher_id == teacher.id,
            OmrAttempt.exam_code_detected == EXAM_CODE,
        )
    ).all()
    for attempt in stale_attempts:
        db.delete(attempt)
    db.flush()


def main() -> None:
    init_db()
    db = SessionLocal()

    try:
        teacher = db.scalar(select(Teacher).where(Teacher.email == TEACHER_EMAIL))
        if teacher is None:
            teacher = Teacher(
                external_uuid="teacher-dummy-40-v1",
                email=TEACHER_EMAIL,
                first_name="Docente",
                last_name="Dummy40",
            )
            db.add(teacher)
            db.flush()

        _delete_existing_dataset(db=db, teacher=teacher)

        exam = Exam(
            teacher_id=teacher.id,
            exam_code=EXAM_CODE,
            title="Examen Dummy 40 Preguntas",
            description="Dataset dummy para pruebas E2E de banco de items + OMR.",
        )
        db.add(exam)
        db.flush()

        answer_key_base: dict[int, str] = {}
        for q in range(1, TOTAL_QUESTIONS + 1):
            correct = correct_answer_for(q)
            answer_key_base[q] = correct
            item = Item(
                teacher_id=teacher.id,
                statement=f"Pregunta dummy {q}: selecciona la opcion correcta.",
                options=option_set(q),
                correct_answer=correct,
                subject=SUBJECT,
                difficulty=DIFFICULTY,
                metadata_json={
                    "seed_batch": SEED_BATCH,
                    "question_number": q,
                    "created_by": "reseed_dummy_dataset.py",
                },
            )
            db.add(item)
            db.flush()

            db.add(
                ExamItem(
                    exam_id=exam.id,
                    item_id=item.id,
                    order_position=q,
                )
            )

        db.flush()

        exam_items = db.scalars(
            select(ExamItem)
            .where(ExamItem.exam_id == exam.id)
            .order_by(ExamItem.order_position.asc())
        ).all()
        published = publish_exam_version(
            exam_items=exam_items,
            seed_shuffle=VERSION_SEED,
            shuffle_questions=True,
            shuffle_options=True,
        )

        exam_version = ExamVersion(
            exam_id=exam.id,
            version_code=VERSION_CODE,
            seed_shuffle=VERSION_SEED,
            shuffle_questions=True,
            shuffle_options=True,
            answer_key_json=published.answer_key,
        )
        db.add(exam_version)
        db.flush()

        for row in published.rows:
            db.add(
                ExamVersionItem(
                    exam_version_id=exam_version.id,
                    source_exam_item_id=row.source_exam_item_id,
                    item_id=row.item_id,
                    question_number=row.question_number,
                    option_map_json=row.option_map,
                    correct_answer_original=row.correct_answer_original,
                    correct_answer_mapped=row.correct_answer_mapped,
                )
            )

        db.commit()

        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "teacher": {"id": teacher.id, "email": teacher.email},
            "exam": {
                "id": exam.id,
                "exam_code": exam.exam_code,
                "title": exam.title,
                "total_questions": TOTAL_QUESTIONS,
            },
            "version": {
                "id": exam_version.id,
                "version_code": exam_version.version_code,
                "seed_shuffle": exam_version.seed_shuffle,
            },
            "answer_key_base_compact": "".join(
                answer_key_base[i] for i in range(1, TOTAL_QUESTIONS + 1)
            ),
            "answer_key_version_sample": {
                "1": exam_version.answer_key_json.get("1"),
                "2": exam_version.answer_key_json.get("2"),
                "3": exam_version.answer_key_json.get("3"),
            },
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
