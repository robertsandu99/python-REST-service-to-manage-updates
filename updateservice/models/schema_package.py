import re
from typing import Optional

from pydantic import BaseModel, validator


class AppIdSchema(BaseModel):
    id: int

    class Config:
        orm_mode = True


class PackageBase(BaseModel):
    id: int
    version: Optional[str]
    description: Optional[str]
    file: Optional[str]
    url: Optional[str]
    hash: Optional[str]
    size: Optional[int]
    application: AppIdSchema

    class Config:
        orm_mode = True


class PackageCreate(BaseModel):
    version: str
    description: Optional[str]

    @validator("version")
    def version_template(cls, version):
        template = r"^\d+\.\d+\.\d+$"
        if not re.match(template, version):
            raise ValueError("Invalid version format")
        return version

    class Config:
        orm_mode = True


class PackageList(BaseModel):
    id: int
    version: Optional[str]
    description: Optional[str]
    application: AppIdSchema

    class Config:
        orm_mode = True
