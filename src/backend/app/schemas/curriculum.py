from __future__ import annotations

from pydantic import BaseModel


class StandardRefRead(BaseModel):
    id: int
    code: str
    name: str


class CompetencyRefRead(BaseModel):
    id: int
    standard_id: int
    standard_code: str
    code: str
    name: str

