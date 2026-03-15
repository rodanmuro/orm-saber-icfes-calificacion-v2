from __future__ import annotations

from pydantic import BaseModel


class StandardRefRead(BaseModel):
    id: int
    name: str


class CompetencyRefRead(BaseModel):
    id: int
    standard_id: int
    name: str
