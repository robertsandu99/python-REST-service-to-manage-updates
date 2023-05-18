from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from updateservice.models.schema_application import (
    ApplicationBase,
    ApplicationBaseGet,
    ApplicationCreate,
    ApplicationPatch,
)
from updateservice.repositories.application_repo import ApplicationRepo
from updateservice.settings import setting
from updateservice.utils.exceptions import (
    ApplicationNotFoundError,
    InvalidIdError,
    TeamIdError,
)

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
    "/v1/teams/{team_id}/applications",
    response_model=ApplicationBase,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_application(
    team_id: int,
    app: ApplicationCreate,
    db_session: ApplicationRepo = Depends(ApplicationRepo),
):
    try:
        created_application = await db_session.create_application(team_id, app)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="An application with the same name already exists"
        )
    return created_application


@router.get(
    "/v1/teams/{team_id}/applications",
    response_model=List[ApplicationBase],
    status_code=status.HTTP_200_OK,
)
async def applications_list(
    team_id: int,
    page: int,
    size: int,
    search: str = None,
    db_session: ApplicationRepo = Depends(ApplicationRepo),
    offset: int = Depends(pagination_offset),
):
    try:
        get_apps_list = await db_session.get_applications_list(
            team_id, limit=size, offset=offset, search=search
        )
        if not get_apps_list and page >= 1:
            raise HTTPException(
                status_code=404, detail="This page has no items to display"
            )
    except TeamIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ApplicationNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return get_apps_list


@router.patch(
    "/v1/team/{team_id}/applications/{application_id}",
    response_model=ApplicationBase,
    status_code=status.HTTP_200_OK,
)
async def update_application_details(
    team_id: int,
    application_id: int,
    app: ApplicationPatch,
    db_session: ApplicationRepo = Depends(ApplicationRepo),
):
    if not app.dict(exclude_unset=True):
        raise HTTPException(
            status_code=422, detail="At least on field has to be present"
        )
    try:
        updated_app = await db_session.patch_application(team_id, application_id, app)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Application name already exists")
    return updated_app


@router.get(
    "/v1/teams/{team_id}/applications/{application_id}",
    response_model=ApplicationBaseGet,
    status_code=status.HTTP_200_OK,
)
async def get_application_details(
    team_id: int,
    application_id: int,
    db_session: ApplicationRepo = Depends(ApplicationRepo),
):
    try:
        get_application, groups_ids = await db_session.get_app(team_id, application_id)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return ApplicationBaseGet(
        id=get_application.id,
        name=get_application.name,
        description=get_application.description,
        team=get_application.team,
        group=groups_ids,
    )
