from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.models import Competency, Standard
from app.db.session import get_db
from app.schemas.curriculum import CompetencyRefRead, StandardRefRead

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.get("/standards", response_model=list[StandardRefRead])
def list_standards(
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[StandardRefRead]:
    query: Select[tuple[Standard]] = select(Standard).order_by(Standard.code.asc())
    term = q.strip()
    if term:
        like = f"%{term}%"
        query = query.where((Standard.code.ilike(like)) | (Standard.name.ilike(like)))
    rows = db.scalars(query.limit(limit)).all()
    return [StandardRefRead(id=row.id, code=row.code, name=row.name) for row in rows]


@router.get("/competencies", response_model=list[CompetencyRefRead])
def list_competencies(
    standard_id: int | None = Query(default=None, ge=1),
    standard_code: str | None = Query(default=None, max_length=64),
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[CompetencyRefRead]:
    resolved_standard_id = standard_id
    if resolved_standard_id is None and standard_code:
        standard = db.scalar(select(Standard).where(Standard.code == standard_code.strip()))
        if standard is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"standard_code={standard_code} not found",
            )
        resolved_standard_id = standard.id

    query = (
        select(Competency, Standard.code)
        .join(Standard, Competency.standard_id == Standard.id)
        .order_by(Competency.code.asc())
    )
    if resolved_standard_id is not None:
        query = query.where(Competency.standard_id == resolved_standard_id)

    term = q.strip()
    if term:
        like = f"%{term}%"
        query = query.where((Competency.code.ilike(like)) | (Competency.name.ilike(like)))

    rows = db.execute(query.limit(limit)).all()
    return [
        CompetencyRefRead(
            id=competency.id,
            standard_id=competency.standard_id,
            standard_code=standard_code_row,
            code=competency.code,
            name=competency.name,
        )
        for competency, standard_code_row in rows
    ]

