from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    id: Optional[str]
    email: str
    full_name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: str
    full_name: str

    class Config:
        orm_mode = True


class TeamBase(BaseModel):
    id: Optional[int]
    name: str
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class TeamCreate(BaseModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class TeamUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True
