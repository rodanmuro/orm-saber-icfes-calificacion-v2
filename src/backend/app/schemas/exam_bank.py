from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExamCreate(BaseModel):
    teacher_id: int = Field(gt=0)
    exam_code: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ExamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: int
    exam_code: str
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class ExamItemBindRequest(BaseModel):
    item_id: int = Field(gt=0)
    order_position: int | None = Field(default=None, gt=0)


class ExamItemRead(BaseModel):
    exam_id: int
    item_id: int
    order_position: int
    item_statement: str


class ExamDetailRead(ExamRead):
    items: list[ExamItemRead]

