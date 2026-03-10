from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.init_db import init_db
from app.db.models import Exam, ExamItem, Item, Teacher
from app.db.session import SessionLocal

SEED_BATCH = "dummy_exam_40_v1"
TEACHER_EMAIL = "docente.dummy40@omr.local"
EXAM_CODE = "1234"
TOTAL_QUESTIONS = 40
SUBJECT = "dummy"
DIFFICULTY = "baja"


def option_set(n: int) -> dict[str, str]:
    return {
        "A": f"Opcion A de la pregunta {n}",
        "B": f"Opcion B de la pregunta {n}",
        "C": f"Opcion C de la pregunta {n}",
        "D": f"Opcion D de la pregunta {n}",
    }


def correct_answer_for(n: int) -> str:
    # Patron deterministico A, B, C, D repetido
    return ["A", "B", "C", "D"][(n - 1) % 4]


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

        # Limpieza idempotente del examen dummy previo
        old_exam = db.scalar(
            select(Exam).where(Exam.teacher_id == teacher.id, Exam.exam_code == EXAM_CODE)
        )
        if old_exam is not None:
            db.delete(old_exam)
            db.flush()

        # Limpieza de items dummy previos de este lote
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

        exam = Exam(
            teacher_id=teacher.id,
            exam_code=EXAM_CODE,
            title="Examen Dummy 40 Preguntas",
            description="Dataset dummy para pruebas E2E de banco de items + OMR.",
        )
        db.add(exam)
        db.flush()

        answer_key: dict[int, str] = {}
        for q in range(1, TOTAL_QUESTIONS + 1):
            correct = correct_answer_for(q)
            answer_key[q] = correct
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
                    "created_by": "seed_dummy_exam_40.py",
                },
            )
            db.add(item)
            db.flush()

            exam_item = ExamItem(
                exam_id=exam.id,
                item_id=item.id,
                order_position=q,
            )
            db.add(exam_item)

        db.commit()

        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "teacher": {
                "id": teacher.id,
                "email": teacher.email,
            },
            "exam": {
                "id": exam.id,
                "exam_code": exam.exam_code,
                "title": exam.title,
                "total_questions": TOTAL_QUESTIONS,
            },
            "answer_key": {str(k): v for k, v in answer_key.items()},
            "answer_key_compact": "".join(answer_key[i] for i in range(1, TOTAL_QUESTIONS + 1)),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
