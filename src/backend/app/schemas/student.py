from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_uuid: str
    document_type: str
    document_number: str
    email: str | None
    first_name: str
    last_name: str
    group_name: str
    created_at: datetime
    updated_at: datetime
