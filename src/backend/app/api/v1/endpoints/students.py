from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Student
from app.db.session import get_db
from app.schemas.student import StudentRead

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentRead])
def list_students(
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[StudentRead]:
    students = db.scalars(
        select(Student)
        .order_by(Student.last_name.asc(), Student.first_name.asc(), Student.id.asc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [StudentRead.model_validate(student) for student in students]
