from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Competency, ExamItem, ExamVersion, ExamVersionItem, Item, Standard, Teacher
from app.db.session import get_db
from app.schemas.item_bank import CurriculumRef, ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


def _resolve_curriculum(
    db: Session,
    curriculum: CurriculumRef | None,
) -> tuple[Standard | None, Competency | None]:
    if curriculum is None:
        return None, None

    standard: Standard | None = None
    competency: Competency | None = None

    if curriculum.standard_name:
        standard = db.scalar(select(Standard).where(Standard.name == curriculum.standard_name))
        if standard is None:
            standard = Standard(name=curriculum.standard_name)
            db.add(standard)
            db.flush()

    if curriculum.competency_name:
        if standard is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="competency_name requires standard_name",
            )
        competency = db.scalar(
            select(Competency).where(
                Competency.standard_id == standard.id,
                Competency.name == curriculum.competency_name,
            )
        )
        if competency is None:
            competency = Competency(standard_id=standard.id, name=curriculum.competency_name)
            db.add(competency)
            db.flush()

    return standard, competency


def _to_item_read(item: Item) -> ItemRead:
    curriculum = None
    if item.standard or item.competency:
        curriculum = CurriculumRef(
            standard_name=item.standard.name if item.standard else None,
            competency_name=item.competency.name if item.competency else None,
        )

    return ItemRead(
        id=item.id,
        teacher_id=item.teacher_id,
        statement=item.statement,
        options=item.options,
        correct_answer=item.correct_answer,  # type: ignore[arg-type]
        subject=item.subject,
        difficulty=item.difficulty,
        curriculum=curriculum,
        metadata=item.metadata_json,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> ItemRead:
    teacher = db.get(Teacher, payload.teacher_id)
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"teacher_id={payload.teacher_id} not found",
        )

    standard, competency = _resolve_curriculum(db=db, curriculum=payload.curriculum)
    item = Item(
        teacher_id=payload.teacher_id,
        statement=payload.statement.strip(),
        options=payload.options,
        correct_answer=payload.correct_answer,
        subject=payload.subject,
        difficulty=payload.difficulty,
        standard_id=standard.id if standard else None,
        competency_id=competency.id if competency else None,
        metadata_json=payload.metadata,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_item_read(item)


@router.get("", response_model=list[ItemRead])
def list_items(db: Session = Depends(get_db)) -> list[ItemRead]:
    statement = select(Item).order_by(Item.id.asc())
    items = db.scalars(statement).all()
    return [_to_item_read(item) for item in items]


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ItemRead:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return _to_item_read(item)


@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)) -> ItemRead:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")

    standard, competency = _resolve_curriculum(db=db, curriculum=payload.curriculum)
    item.statement = payload.statement.strip()
    item.options = payload.options
    item.correct_answer = payload.correct_answer
    item.subject = payload.subject
    item.difficulty = payload.difficulty
    item.standard_id = standard.id if standard else None
    item.competency_id = competency.id if competency else None
    item.metadata_json = payload.metadata
    db.commit()
    db.refresh(item)
    return _to_item_read(item)


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> Response:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")

    try:
        if force:
            linked_exam_items = db.scalars(select(ExamItem).where(ExamItem.item_id == item_id)).all()
            linked_exam_item_ids = [row.id for row in linked_exam_items]
            linked_exam_ids = sorted({row.exam_id for row in linked_exam_items})

            db.execute(delete(ExamVersionItem).where(ExamVersionItem.item_id == item_id))

            if linked_exam_item_ids:
                db.execute(
                    delete(ExamVersionItem).where(
                        ExamVersionItem.source_exam_item_id.in_(linked_exam_item_ids)
                    )
                )

            if linked_exam_ids:
                db.execute(delete(ExamVersion).where(ExamVersion.exam_id.in_(linked_exam_ids)))

            db.execute(delete(ExamItem).where(ExamItem.item_id == item_id))

        db.delete(item)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="item is linked to exam/exam_version and cannot be deleted",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
