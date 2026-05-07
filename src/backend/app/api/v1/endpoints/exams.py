from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Exam, ExamItem, ExamVersion, ExamVersionItem, Item, Teacher
from app.db.session import get_db
from app.modules.exam_version.service import publish_exam_version
from app.modules.exam_export.pdf_service import build_exam_version_pdf
from app.modules.exam_export.docx_service import build_exam_version_docx
from app.modules.omr_scoring.service import build_answer_key_from_exam_items
from app.schemas.exam_bank import (
    ExamCreate,
    ExamDetailRead,
    ExamItemBindRequest,
    ExamItemRead,
    ExamRead,
    ExamVersionDetailRead,
    ExamVersionItemRead,
    ExamVersionPublishRequest,
    ExamVersionRead,
    ExamVersionReorderRequest,
)

router = APIRouter(prefix="/exams", tags=["exams"])


def _resolve_exam_code(db: Session, teacher_id: int, requested: str | None) -> str:
    if requested is not None and requested.strip():
        return requested.strip()

    used_codes = set(
        db.scalars(select(Exam.exam_code).where(Exam.teacher_id == teacher_id)).all()
    )
    candidate = 1
    while str(candidate) in used_codes:
        candidate += 1
    return str(candidate)


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


def _exam_version_to_read(version: ExamVersion) -> ExamVersionRead:
    return ExamVersionRead(
        id=version.id,
        exam_id=version.exam_id,
        teacher_id=version.teacher_id,
        exam_code=version.exam_code,
        version_code=version.version_code,
        seed_shuffle=version.seed_shuffle,
        shuffle_questions=version.shuffle_questions,
        shuffle_options=version.shuffle_options,
        answer_key=version.answer_key_json,
        created_at=version.created_at,
    )


def _exam_version_to_detail(
    version: ExamVersion,
    version_items: list[ExamVersionItem],
) -> ExamVersionDetailRead:
    return ExamVersionDetailRead(
        **_exam_version_to_read(version).model_dump(),
        items=[
            ExamVersionItemRead(
                id=row.id,
                question_number=row.question_number,
                source_exam_item_id=row.source_exam_item_id,
                item_id=row.item_id,
                option_map=row.option_map_json,
                correct_answer_original=row.correct_answer_original,
                correct_answer_mapped=row.correct_answer_mapped,
            )
            for row in version_items
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

    exam_code = _resolve_exam_code(db=db, teacher_id=payload.teacher_id, requested=payload.exam_code)

    exam = Exam(
        teacher_id=payload.teacher_id,
        exam_code=exam_code,
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


def _resolve_version_code(db: Session, exam_id: int, requested: str | None) -> str:
    if requested:
        return requested.strip()
    count = db.scalar(select(func.count(ExamVersion.id)).where(ExamVersion.exam_id == exam_id)) or 0
    return str(count + 1)


def _resolve_version_exam_code(db: Session, teacher_id: int) -> str:
    used_exam_codes = set(
        db.scalars(select(Exam.exam_code).where(Exam.teacher_id == teacher_id)).all()
    )
    used_version_codes = set(
        db.scalars(select(ExamVersion.exam_code).where(ExamVersion.teacher_id == teacher_id)).all()
    )
    used_codes = {str(code) for code in used_exam_codes.union(used_version_codes)}

    candidate = 1
    while str(candidate) in used_codes:
        candidate += 1
    return str(candidate)


@router.post(
    "/{exam_id}/versions/publish",
    response_model=ExamVersionDetailRead,
    status_code=status.HTTP_201_CREATED,
)
def publish_version(
    exam_id: int,
    payload: ExamVersionPublishRequest,
    db: Session = Depends(get_db),
) -> ExamVersionDetailRead:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")

    exam_items = db.scalars(
        select(ExamItem)
        .where(ExamItem.exam_id == exam_id)
        .order_by(ExamItem.order_position.asc())
    ).all()
    if not exam_items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="cannot publish a version for an exam without items",
        )

    version_code = _resolve_version_code(db=db, exam_id=exam_id, requested=payload.version_code)
    seed_shuffle = payload.seed_shuffle
    if seed_shuffle is None:
        seed_shuffle = int(datetime.now().timestamp())

    published = publish_exam_version(
        exam_items=exam_items,
        seed_shuffle=seed_shuffle,
        shuffle_questions=payload.shuffle_questions,
        shuffle_options=payload.shuffle_options,
    )

    version = ExamVersion(
        exam_id=exam_id,
        teacher_id=exam.teacher_id,
        exam_code=_resolve_version_exam_code(db=db, teacher_id=exam.teacher_id),
        version_code=version_code,
        seed_shuffle=seed_shuffle,
        shuffle_questions=payload.shuffle_questions,
        shuffle_options=payload.shuffle_options,
        answer_key_json=published.answer_key,
    )
    db.add(version)
    db.flush()

    for row in published.rows:
        db.add(
            ExamVersionItem(
                exam_version_id=version.id,
                source_exam_item_id=row.source_exam_item_id,
                item_id=row.item_id,
                question_number=row.question_number,
                option_map_json=row.option_map,
                correct_answer_original=row.correct_answer_original,
                correct_answer_mapped=row.correct_answer_mapped,
            )
        )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="version_code or exam_code already exists",
        ) from None
    db.refresh(version)

    version_items = db.scalars(
        select(ExamVersionItem)
        .where(ExamVersionItem.exam_version_id == version.id)
        .order_by(ExamVersionItem.question_number.asc())
    ).all()
    return _exam_version_to_detail(version=version, version_items=version_items)


@router.get("/{exam_id}/versions", response_model=list[ExamVersionRead])
def list_exam_versions(exam_id: int, db: Session = Depends(get_db)) -> list[ExamVersionRead]:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")
    rows = db.scalars(
        select(ExamVersion)
        .where(ExamVersion.exam_id == exam_id)
        .order_by(ExamVersion.id.asc())
    ).all()
    return [_exam_version_to_read(row) for row in rows]


@router.get("/{exam_id}/versions/{version_id}", response_model=ExamVersionDetailRead)
def get_exam_version(exam_id: int, version_id: int, db: Session = Depends(get_db)) -> ExamVersionDetailRead:
    version = db.get(ExamVersion, version_id)
    if version is None or version.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam version not found")
    version_items = db.scalars(
        select(ExamVersionItem)
        .where(ExamVersionItem.exam_version_id == version_id)
        .order_by(ExamVersionItem.question_number.asc())
    ).all()
    return _exam_version_to_detail(version=version, version_items=version_items)


@router.patch("/{exam_id}/versions/{version_id}/reorder", response_model=ExamVersionDetailRead)
def reorder_exam_version(
    exam_id: int,
    version_id: int,
    payload: ExamVersionReorderRequest,
    db: Session = Depends(get_db),
) -> ExamVersionDetailRead:
    version = db.get(ExamVersion, version_id)
    if version is None or version.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam version not found")

    version_items = db.scalars(
        select(ExamVersionItem)
        .where(ExamVersionItem.exam_version_id == version_id)
        .order_by(ExamVersionItem.question_number.asc())
    ).all()
    if not version_items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="cannot reorder an empty exam version",
        )

    current_ids = [row.id for row in version_items]
    requested_ids = payload.ordered_version_item_ids
    if len(requested_ids) != len(current_ids) or set(requested_ids) != set(current_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ordered_version_item_ids must contain exactly the same version item ids",
        )

    by_id = {row.id: row for row in version_items}
    reordered_rows = [by_id[row_id] for row_id in requested_ids]

    # Two-phase renumbering to avoid transient unique collisions on
    # (exam_version_id, question_number) while swapping positions.
    offset = len(reordered_rows) + 1000
    for row in reordered_rows:
        row.question_number = row.question_number + offset
    db.flush()

    answer_key: dict[str, str] = {}
    for idx, row in enumerate(reordered_rows, start=1):
        row.question_number = idx
        answer_key[str(idx)] = row.correct_answer_mapped

    version.answer_key_json = answer_key
    db.add(version)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="could not reorder exam version due to concurrent/conflicting update",
        ) from exc
    db.refresh(version)

    refreshed = db.scalars(
        select(ExamVersionItem)
        .where(ExamVersionItem.exam_version_id == version_id)
        .order_by(ExamVersionItem.question_number.asc())
    ).all()
    return _exam_version_to_detail(version=version, version_items=refreshed)


@router.get("/{exam_id}/versions/{version_id}/export/pdf")
def export_exam_version_pdf(exam_id: int, version_id: int, db: Session = Depends(get_db)) -> Response:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")

    version = db.get(ExamVersion, version_id)
    if version is None or version.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam version not found")

    version_items = db.scalars(
        select(ExamVersionItem)
        .where(ExamVersionItem.exam_version_id == version_id)
        .order_by(ExamVersionItem.question_number.asc())
    ).all()
    if not version_items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="cannot export an empty exam version",
        )

    item_ids = {row.item_id for row in version_items}
    items_by_id = {
        item.id: item
        for item in db.scalars(select(Item).where(Item.id.in_(item_ids))).all()
    }

    pdf_bytes = build_exam_version_pdf(
        exam=exam,
        version=version,
        version_items=version_items,
        items_by_id=items_by_id,
    )
    filename = f"cuadernillo_exam_{version.exam_code}_{version.version_code}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


@router.get("/{exam_id}/versions/{version_id}/export/docx")
def export_exam_version_docx(exam_id: int, version_id: int, db: Session = Depends(get_db)) -> Response:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam not found")

    version = db.get(ExamVersion, version_id)
    if version is None or version.exam_id != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="exam version not found")

    version_items = db.scalars(
        select(ExamVersionItem)
        .where(ExamVersionItem.exam_version_id == version_id)
        .order_by(ExamVersionItem.question_number.asc())
    ).all()
    if not version_items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="cannot export an empty exam version",
        )

    item_ids = {row.item_id for row in version_items}
    items_by_id = {
        item.id: item
        for item in db.scalars(select(Item).where(Item.id.in_(item_ids))).all()
    }

    docx_bytes = build_exam_version_docx(
        exam=exam,
        version=version,
        version_items=version_items,
        items_by_id=items_by_id,
    )
    filename = f"cuadernillo_exam_{version.exam_code}_{version.version_code}.docx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )
