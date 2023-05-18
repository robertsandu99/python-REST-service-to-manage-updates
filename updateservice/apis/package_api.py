from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from updateservice.models.schema_package import PackageBase, PackageCreate, PackageList
from updateservice.repositories.application_repo import ApplicationRepo
from updateservice.repositories.package_repo import (
    DownloadPackageRepo,
    PackageRepo,
    UpdatePackageRepo,
)
from updateservice.settings import setting
from updateservice.utils.exceptions import InvalidIdError

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
    "/v1/applications/{application_id}/packages",
    response_model=PackageBase,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_package(
    application_id: int,
    package: PackageCreate,
    db_session: PackageRepo = Depends(PackageRepo),
):
    try:
        created_package = await db_session.create_package(application_id, package)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return created_package


@router.delete(
    "/v1/applications/{application_id}/packages/{package_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_a_package(
    application_id: int, package_id: int, db_session: PackageRepo = Depends(PackageRepo)
):
    try:
        deleted_package = await db_session.delete_package(application_id, package_id)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return deleted_package


@router.get(
    "/v1/applications/{application_id}/packages/{package_id}",
    response_model=PackageBase,
    status_code=status.HTTP_200_OK,
)
async def get_package_details(
    application_id: int, package_id: int, db_session: PackageRepo = Depends(PackageRepo)
):
    try:
        the_package = await db_session.get_package(application_id, package_id)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return the_package


@router.get(
    "/v1/applications/{application_id}/packages",
    response_model=List[PackageList],
    status_code=status.HTTP_200_OK,
)
async def list_of_packages(
    application_id: int,
    page: int,
    size: int,
    db_session: PackageRepo = Depends(PackageRepo),
    app_exists: ApplicationRepo = Depends(ApplicationRepo),
    offset: int = Depends(pagination_offset),
):
    try:
        await app_exists.check_app_exists(application_id)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    try:
        packages_list = await db_session.list_packages(
            application_id, limit=size, offset=offset
        )
        if not packages_list and page >= 1:
            raise HTTPException(
                status_code=404, detail="This page has no items to display"
            )
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return packages_list


@router.post(
    "/v1/applications/{application_id}/packages/{package_id}/file",
    response_model=PackageBase,
    status_code=status.HTTP_200_OK,
)
async def upload_a_file(
    application_id: int,
    package_id: int,
    file: UploadFile = File(...),
    db_session: UpdatePackageRepo = Depends(UpdatePackageRepo),
):
    try:
        updated_package = await db_session.update_package(
            application_id, package_id, file
        )
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    return updated_package


@router.get(
    "/v1/applications/{application_id}/packages/{package_id}/file",
    status_code=status.HTTP_200_OK,
)
async def download_a_file(
    application_id: int,
    package_id: int,
    db_session: DownloadPackageRepo = Depends(DownloadPackageRepo),
):
    try:
        location, download_file = await db_session.download_package(
            application_id, package_id
        )
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return FileResponse(location, filename=download_file)
