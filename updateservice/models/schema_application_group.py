from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
    name: str = Field(..., max_length=255)

    class Config:
        orm_mode = True


class GroupBase(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ApplicationGroupBase(BaseModel):
    id: int
    application_id: int
    group_id: int

    class Config:
        orm_mode = True
