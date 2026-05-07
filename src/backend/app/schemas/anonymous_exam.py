from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AnonymousExamCreate(BaseModel):
    teacher_id: int = Field(gt=0)
    exam_code: str | None = Field(default=None, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    question_count: int = Field(ge=1, le=200)
    answer_key: dict[str, str]
    source_pdf_path: str | None = None
    is_active: bool = True

    @field_validator("answer_key")
    @classmethod
    def validate_answer_key(cls, value: dict[str, str]) -> dict[str, str]:
        if not value:
            raise ValueError("answer_key must not be empty")
        normalized: dict[str, str] = {}
        for raw_qn, raw_ans in value.items():
            qn = str(raw_qn).strip()
            if not qn.isdigit() or int(qn) <= 0:
                raise ValueError("answer_key keys must be positive integer strings")
            ans = str(raw_ans).strip().upper()
            if ans not in {"A", "B", "C", "D"}:
                raise ValueError(f"invalid answer for question {qn}")
            normalized[str(int(qn))] = ans
        return normalized


class AnonymousExamUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    question_count: int | None = Field(default=None, ge=1, le=200)
    answer_key: dict[str, str] | None = None
    source_pdf_path: str | None = None
    is_active: bool | None = None

    @field_validator("answer_key")
    @classmethod
    def validate_answer_key(cls, value: dict[str, str] | None) -> dict[str, str] | None:
        if value is None:
            return None
        normalized: dict[str, str] = {}
        for raw_qn, raw_ans in value.items():
            qn = str(raw_qn).strip()
            if not qn.isdigit() or int(qn) <= 0:
                raise ValueError("answer_key keys must be positive integer strings")
            ans = str(raw_ans).strip().upper()
            if ans not in {"A", "B", "C", "D"}:
                raise ValueError(f"invalid answer for question {qn}")
            normalized[str(int(qn))] = ans
        return normalized


class AnonymousExamRead(BaseModel):
    id: int
    teacher_id: int
    exam_code: str
    title: str
    question_count: int
    answer_key: dict[str, str]
    source_pdf_path: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

