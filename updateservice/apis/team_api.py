from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from updateservice.models.schema import TeamBase, TeamCreate, TeamUpdate
from updateservice.repositories.team_repo import GetTeamRepo, PutTeamRepo, TeamRepo
from updateservice.settings import setting

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
    "/internal/v1/teams", response_model=TeamBase, status_code=status.HTTP_201_CREATED
)
async def create_new_team(
    newteam: TeamCreate, db_session: TeamRepo = Depends(TeamRepo)
):
    try:
        created_team = await db_session.create_team(newteam)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="This team already exists")
    return created_team


@router.get(
    "/internal/v1/teams", response_model=List[TeamBase], status_code=status.HTTP_200_OK
)
async def get_list_of_teams(
    page: int,
    size: int,
    offset: int = Depends(pagination_offset),
    get_team_repo: GetTeamRepo = Depends(GetTeamRepo),
):
    list_of_all_teams = await get_team_repo.get_all_teams(limit=size, offset=offset)
    if not list_of_all_teams and page >= 1:
        raise HTTPException(status_code=404, detail="This page has no items to display")
    return list_of_all_teams


@router.put(
    "/internal/v1/teams/{team_id}",
    response_model=TeamBase,
    status_code=status.HTTP_200_OK,
)
async def update_a_team_by_id(
    team_id: int, team: TeamUpdate, update_team_repo: PutTeamRepo = Depends(PutTeamRepo)
):
    try:
        the_updated_team = await update_team_repo.update_team(team_id, team)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Team name already exists")
    return the_updated_team
