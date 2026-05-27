from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExamCreate(BaseModel):
    teacher_id: int = Field(gt=0)
    exam_code: str | None = Field(default=None, max_length=64)
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
    group_key: str | None = Field(default=None, max_length=64)

    @field_validator("group_key")
    @classmethod
    def validate_group_key(cls, value: str | None) -> str | None:
        normalized = str(value or "").strip()
        if not normalized:
            return None
        if not normalized.isdigit():
            raise ValueError("group_key must be a positive integer")
        parsed = int(normalized)
        if parsed <= 0:
            raise ValueError("group_key must be a positive integer")
        return str(parsed)


class ExamItemUpdateRequest(BaseModel):
    group_key: str | None = Field(default=None, max_length=64)

    @field_validator("group_key")
    @classmethod
    def validate_group_key(cls, value: str | None) -> str | None:
        normalized = str(value or "").strip()
        if not normalized:
            return None
        if not normalized.isdigit():
            raise ValueError("group_key must be a positive integer")
        parsed = int(normalized)
        if parsed <= 0:
            raise ValueError("group_key must be a positive integer")
        return str(parsed)


class ExamItemRead(BaseModel):
    exam_id: int
    item_id: int
    order_position: int
    group_key: str | None
    item_statement: str


class ExamDetailRead(ExamRead):
    items: list[ExamItemRead]


class ExamVersionPublishRequest(BaseModel):
    version_code: str | None = Field(default=None, min_length=1, max_length=64)
    seed_shuffle: int | None = Field(default=None)
    shuffle_questions: bool = True
    shuffle_options: bool = True


class ExamVersionItemRead(BaseModel):
    id: int
    question_number: int
    source_exam_item_id: int
    item_id: int
    option_map: dict[str, str]
    correct_answer_original: str
    correct_answer_mapped: str


class ExamVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exam_id: int
    teacher_id: int
    exam_code: str
    version_code: str
    seed_shuffle: int
    shuffle_questions: bool
    shuffle_options: bool
    answer_key: dict[str, str]
    created_at: datetime


class ExamVersionDetailRead(ExamVersionRead):
    items: list[ExamVersionItemRead]


class ExamVersionReorderRequest(BaseModel):
    ordered_version_item_ids: list[int] = Field(min_length=1)
