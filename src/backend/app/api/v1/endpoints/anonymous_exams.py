from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import AnonymousExam, Teacher
from app.db.session import get_db
from app.schemas.anonymous_exam import AnonymousExamCreate, AnonymousExamRead, AnonymousExamUpdate

router = APIRouter(prefix="/anonymous-exams", tags=["anonymous-exams"])


def _resolve_exam_code(db: Session, teacher_id: int, requested: str | None) -> str:
    if requested is not None and requested.strip():
        return requested.strip()
    used_codes = set(
        db.scalars(select(AnonymousExam.exam_code).where(AnonymousExam.teacher_id == teacher_id)).all()
    )
    candidate = 1
    while str(candidate) in used_codes:
        candidate += 1
    return str(candidate)


def _to_read(row: AnonymousExam) -> AnonymousExamRead:
    return AnonymousExamRead(
        id=row.id,
        teacher_id=row.teacher_id,
        exam_code=row.exam_code,
        title=row.title,
        question_count=row.question_count,
        answer_key=row.answer_key_json,
        source_pdf_path=row.source_pdf_path,
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.post("", response_model=AnonymousExamRead, status_code=status.HTTP_201_CREATED)
def create_anonymous_exam(payload: AnonymousExamCreate, db: Session = Depends(get_db)) -> AnonymousExamRead:
    teacher = db.get(Teacher, payload.teacher_id)
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="teacher not found")

    if len(payload.answer_key) != payload.question_count:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="question_count must match answer_key size",
        )
    required = {str(i) for i in range(1, payload.question_count + 1)}
    provided = set(payload.answer_key.keys())
    if required != provided:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="answer_key must contain consecutive questions from 1..question_count",
        )

    exam_code = _resolve_exam_code(db, payload.teacher_id, payload.exam_code)
    row = AnonymousExam(
        teacher_id=payload.teacher_id,
        exam_code=exam_code,
        title=payload.title.strip(),
        question_count=payload.question_count,
        answer_key_json=payload.answer_key,
        source_pdf_path=payload.source_pdf_path,
        is_active=payload.is_active,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="exam_code already exists") from None
    db.refresh(row)
    return _to_read(row)


@router.get("", response_model=list[AnonymousExamRead])
def list_anonymous_exams(
    teacher_id: int | None = Query(default=None, gt=0),
    only_active: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[AnonymousExamRead]:
    stmt = select(AnonymousExam).order_by(AnonymousExam.id.asc())
    if teacher_id is not None:
        stmt = stmt.where(AnonymousExam.teacher_id == teacher_id)
    if only_active:
        stmt = stmt.where(AnonymousExam.is_active.is_(True))
    rows = db.scalars(stmt).all()
    return [_to_read(row) for row in rows]


@router.get("/{anonymous_exam_id}", response_model=AnonymousExamRead)
def get_anonymous_exam(anonymous_exam_id: int, db: Session = Depends(get_db)) -> AnonymousExamRead:
    row = db.get(AnonymousExam, anonymous_exam_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="anonymous_exam not found")
    return _to_read(row)


@router.patch("/{anonymous_exam_id}", response_model=AnonymousExamRead)
def update_anonymous_exam(
    anonymous_exam_id: int,
    payload: AnonymousExamUpdate,
    db: Session = Depends(get_db),
) -> AnonymousExamRead:
    row = db.get(AnonymousExam, anonymous_exam_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="anonymous_exam not found")

    if payload.title is not None:
        row.title = payload.title.strip()
    if payload.question_count is not None:
        row.question_count = payload.question_count
    if payload.answer_key is not None:
        row.answer_key_json = payload.answer_key
    if payload.source_pdf_path is not None:
        row.source_pdf_path = payload.source_pdf_path
    if payload.is_active is not None:
        row.is_active = payload.is_active

    if len(row.answer_key_json) != row.question_count:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="question_count must match answer_key size",
        )
    required = {str(i) for i in range(1, row.question_count + 1)}
    provided = set((row.answer_key_json or {}).keys())
    if required != provided:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="answer_key must contain consecutive questions from 1..question_count",
        )

    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_read(row)
