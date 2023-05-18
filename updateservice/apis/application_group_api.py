from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from updateservice.models.schema_application_group import (
    ApplicationGroupBase,
    GroupBase,
    GroupCreate,
)
from updateservice.repositories.application_group_repo import (
    ApplicationGroupRepo,
    GroupRepo,
)
from updateservice.utils.exceptions import (
    AlreadyAssignedError,
    ApplicationAssignedError,
    InvalidIdError,
    NotAssignedError,
)

router = APIRouter()


@router.post(
    "/v1/groups", response_model=GroupBase, status_code=status.HTTP_201_CREATED
)
async def create_new_group(
    group: GroupCreate, db_session: GroupRepo = Depends(GroupRepo)
):

    try:
        created_group = await db_session.create_group(group)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="A group with the same name already exists"
        )
    return created_group


@router.post(
    "/v1/applications/{application_id}/groups/{group_id}",
    response_model=ApplicationGroupBase,
    status_code=status.HTTP_201_CREATED,
)
async def assign_application_to_group(
    application_id: int,
    group_id: int,
    db_session: ApplicationGroupRepo = Depends(ApplicationGroupRepo),
):
    try:
        assign_app_group = await db_session.create_application_group(
            application_id, group_id
        )
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AlreadyAssignedError as e:
        raise HTTPException(status_code=400, detail=e.message)
    return assign_app_group


@router.delete(
    "/v1/groups/{group_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_a_group(
    group_id: int,
    db_session: GroupRepo = Depends(GroupRepo),
):
    try:
        group_deleted = await db_session.delete_group(group_id)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ApplicationAssignedError as e:
        raise HTTPException(status_code=400, detail=e.message)
    return group_deleted


@router.delete("/v1/applications/{application_id}/groups/{group_id}")
async def unassign_application_from_group(
    application_id: int,
    group_id: int,
    db_session: ApplicationGroupRepo = Depends(ApplicationGroupRepo),
):
    try:
        unassigned_app = await db_session.unassign_application(application_id, group_id)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except NotAssignedError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return unassigned_app
