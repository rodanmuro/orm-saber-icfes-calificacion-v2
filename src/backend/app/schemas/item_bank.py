from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ChoiceKey = Literal["A", "B", "C", "D"]


class CurriculumRef(BaseModel):
    standard_code: str | None = None
    standard_name: str | None = None
    competency_code: str | None = None
    competency_name: str | None = None


class ItemBase(BaseModel):
    statement: str = Field(min_length=1)
    options: dict[ChoiceKey, str]
    correct_answer: ChoiceKey
    subject: str | None = None
    difficulty: str | None = None
    curriculum: CurriculumRef | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("options")
    @classmethod
    def validate_options_structure(cls, value: dict[ChoiceKey, str]) -> dict[ChoiceKey, str]:
        expected_keys = {"A", "B", "C", "D"}
        keys = set(value.keys())
        if keys != expected_keys:
            raise ValueError("options must contain exactly A, B, C and D")
        for option_key, option_value in value.items():
            if not option_value or not option_value.strip():
                raise ValueError(f"option {option_key} cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_correct_answer_present(self) -> "ItemBase":
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must exist in options")
        return self


class ItemCreate(ItemBase):
    teacher_id: int = Field(gt=0)


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime

