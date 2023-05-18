from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from updateservice.models.schema import UserBase, UserCreate
from updateservice.repositories.user_repo import UserRepo
from updateservice.settings import setting
from updateservice.utils.exceptions import UsersNotFoundError

router = APIRouter()

max_int = setting["POSTGRES_MAX_INT"]


def pagination_offset(
    page: int = Query(
        default=1, ge=1, le=max_int, description="Insert the number of pages"
    ),
    size: int = Query(
        default=20, ge=1, le=max_int, description="Insert the size of the page"
    ),
):
    offset = (page - 1) * size
    if offset > max_int:
        raise HTTPException(status_code=400, detail="Offset is too big")
    return offset


@router.post(
    "/internal/v1/users", response_model=UserBase, status_code=status.HTTP_201_CREATED
)
async def create_new_user(
    newuser: UserCreate, db_session: UserRepo = Depends(UserRepo)
):
    try:
        created_user = await db_session.create_user(newuser)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="There is already a user registered with this email"
        )
    return created_user


@router.get(
    "/internal/v1/users", response_model=List[UserBase], status_code=status.HTTP_200_OK
)
async def get_list_of_users(
    page: int,
    size: int,
    search: str = None,
    offset: int = Depends(pagination_offset),
    db_session: UserRepo = Depends(UserRepo),
):
    try:
        list_of_all_teams = await db_session.get_list_users(
            limit=size, offset=offset, search=search
        )
        if not list_of_all_teams and page >= 1:
            raise HTTPException(
                status_code=404, detail="This page has no items to display"
            )
        return list_of_all_teams
    except UsersNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
