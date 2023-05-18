from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr


class TokenPayload(BaseModel):
    user_id: int
    token: str

    class Config:
        orm_mode = True


class TokenBase(BaseModel):
    id: Optional[int]
    token: TokenPayload

    class Config:
        orm_mode = True
