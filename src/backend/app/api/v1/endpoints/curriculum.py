from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
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
    query = select(Standard).order_by(Standard.name.asc())
    term = q.strip()
    if term:
        query = query.where(Standard.name.ilike(f"%{term}%"))
    rows = db.scalars(query.limit(limit)).all()
    return [StandardRefRead(id=row.id, name=row.name) for row in rows]


@router.get("/competencies", response_model=list[CompetencyRefRead])
def list_competencies(
    standard_id: int | None = Query(default=None, ge=1),
    q: str = Query(default="", max_length=120),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[CompetencyRefRead]:
    query = select(Competency).order_by(Competency.name.asc())
    if standard_id is not None:
        query = query.where(Competency.standard_id == standard_id)
    term = q.strip()
    if term:
        query = query.where(Competency.name.ilike(f"%{term}%"))
    rows = db.scalars(query.limit(limit)).all()
    return [CompetencyRefRead(id=row.id, standard_id=row.standard_id, name=row.name) for row in rows]
