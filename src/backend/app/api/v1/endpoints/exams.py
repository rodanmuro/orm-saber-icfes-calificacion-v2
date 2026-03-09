from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Exam, ExamItem, Item, Teacher
from app.db.session import get_db
from app.modules.omr_scoring.service import build_answer_key_from_exam_items
from app.schemas.exam_bank import (
    ExamCreate,
    ExamDetailRead,
    ExamItemBindRequest,
    ExamItemRead,
    ExamRead,
)

router = APIRouter(prefix="/exams", tags=["exams"])


def _exam_to_read(exam: Exam) -> ExamRead:
    return ExamRead.model_validate(exam)


def _exam_to_detail(exam: Exam, exam_items: list[ExamItem]) -> ExamDetailRead:
    return ExamDetailRead(
        id=exam.id,
        teacher_id=exam.teacher_id,
        exam_code=exam.exam_code,
        title=exam.title,
        description=exam.description,
        created_at=exam.created_at,
        updated_at=exam.updated_at,
        items=[
            ExamItemRead(
                exam_id=row.exam_id,
                item_id=row.item_id,
                order_position=row.order_position,
                item_statement=row.item.statement,
            )
            for row in exam_items
        ],
    )


@router.post("", response_model=ExamRead, status_code=status.HTTP_201_CREATED)
def create_exam(payload: ExamCreate, db: Session = Depends(get_db)) -> ExamRead:
    teacher = db.get(Teacher, payload.teacher_id)
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"teacher_id={payload.teacher_id} not found",
        )

    exam = Exam(
        teacher_id=payload.teacher_id,
        exam_code=payload.exam_code.strip(),
        title=payload.title.strip(),
        description=payload.description,
    )
    db.add(exam)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="exam_code already exists for this teacher",
        ) from None
    db.refresh(exam)
    return _exam_to_read(exam)


@router.get("", response_model=list[ExamRead])
def list_exams(
    teacher_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> list[ExamRead]:
    statement = select(Exam).order_by(Exam.id.asc())
    if teacher_id is not None:
        statement = statement.where(Exam.teacher_id == teacher_id)
    exams = db.scalars(statement).all()
    return [_exam_to_read(exam) for exam in exams]


@router.get("/{exam_id}", response_model=ExamDetailRead)
def get_exam(exam_id: int, db: Session = Depends(get_db)) -> ExamDetailRead:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")
    exam_items = db.scalars(
        select(ExamItem)
        .where(ExamItem.exam_id == exam_id)
        .order_by(ExamItem.order_position.asc())
    ).all()
    return _exam_to_detail(exam, exam_items)


@router.get("/{exam_id}/answer-key")
def get_exam_answer_key(exam_id: int, db: Session = Depends(get_db)) -> dict:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")
    exam_items = db.scalars(
        select(ExamItem)
        .where(ExamItem.exam_id == exam_id)
        .order_by(ExamItem.order_position.asc())
    ).all()
    return {
        "exam_id": exam.id,
        "teacher_id": exam.teacher_id,
        "exam_code": exam.exam_code,
        "answer_key": build_answer_key_from_exam_items(exam_items),
    }


@router.post("/{exam_id}/items", response_model=ExamDetailRead)
def bind_item_to_exam(
    exam_id: int,
    payload: ExamItemBindRequest,
    db: Session = Depends(get_db),
) -> ExamDetailRead:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")

    item = db.get(Item, payload.item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    if item.teacher_id != exam.teacher_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="item and exam must belong to the same teacher",
        )

    order_position = payload.order_position
    if order_position is None:
        max_order = db.scalar(
            select(func.max(ExamItem.order_position)).where(ExamItem.exam_id == exam_id)
        )
        order_position = (max_order or 0) + 1

    row = ExamItem(
        exam_id=exam_id,
        item_id=payload.item_id,
        order_position=order_position,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="item already bound or order_position already used in this exam",
        ) from None

    return get_exam(exam_id=exam_id, db=db)


@router.delete("/{exam_id}/items/{item_id}", response_model=ExamDetailRead)
def unbind_item_from_exam(exam_id: int, item_id: int, db: Session = Depends(get_db)) -> ExamDetailRead:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")

    row = db.scalar(
        select(ExamItem).where(ExamItem.exam_id == exam_id, ExamItem.item_id == item_id)
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam-item not found")
    db.delete(row)
    db.commit()
    return get_exam(exam_id=exam_id, db=db)
