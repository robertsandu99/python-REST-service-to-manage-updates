from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class TeamIdSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True


class GroupIdSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True


class ApplicationBaseGet(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    team: TeamIdSchema
    group: List[int]

    class Config:
        orm_mode = True


class ApplicationBase(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    team: TeamIdSchema

    class Config:
        orm_mode = True


class ApplicationCreate(BaseModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class ApplicationPatch(BaseModel):
    name: Optional[str]
    description: Optional[str] = Field(max_length=255)

    @validator("name")
    def prevent_none(cls, name):
        if name is None:
            raise ValueError("Name cannot be null")
        return name

    class Config:
        orm_mode = True
