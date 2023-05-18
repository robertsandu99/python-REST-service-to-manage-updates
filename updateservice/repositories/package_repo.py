import hashlib
import os

import aiofiles
import aiofiles.os
from fastapi import File, UploadFile
from sqlalchemy import delete, select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import exists

from updateservice.connection_db import async_session
from updateservice.models.application import Application
from updateservice.models.package import Package
from updateservice.models.schema_package import PackageCreate
from updateservice.utils.exceptions import InvalidAppIdError, InvalidPackageIdError


class PackageRepo:
    async def create_package(self, application_id: int, package=PackageCreate):
        async with async_session() as session:
            query_app = select(exists().where(Application.id == application_id))
            result_app = await session.execute(query_app)
            if not result_app.scalar():
                raise InvalidAppIdError
            new_package = Package(
                application_id=application_id,
                version=package.version,
                description=package.description,
            )
            session.add(new_package)
            await session.commit()
            query_package = await session.execute(
                select(Package)
                .options(joinedload(Package.application))
                .filter(
                    Package.application_id == application_id,
                    Package.version == package.version,
                )
            )
            select_package = query_package.first()
            the_package = dict(select_package).get("Package")
            return the_package

    async def delete_package(self, application_id: int, package_id: int):
        async with async_session() as session:
            query_app = select(exists().where(Application.id == application_id))
            result_app = await session.execute(query_app)
            if not result_app.scalar():
                raise InvalidAppIdError
            query_package = await session.execute(
                select(Package)
                .options(joinedload(Package.application))
                .filter(
                    Package.application_id == application_id, Package.id == package_id
                )
            )
            select_package = query_package.first()
            if not select_package:
                raise InvalidPackageIdError
            delete_package = delete(Package).filter(
                Package.application_id == application_id, Package.id == package_id
            )
            await session.execute(delete_package)
            await session.commit()
            return "Package has been successfully deleted"

    async def get_package(self, application_id: int, package_id: int):
        async with async_session() as session:
            query_app = select(exists().where(Application.id == application_id))
            result_app = await session.execute(query_app)
            if not result_app.scalar():
                raise InvalidAppIdError
            query_package = await session.execute(
                select(Package)
                .options(joinedload(Package.application))
                .filter(
                    Package.application_id == application_id, Package.id == package_id
                )
            )
            select_package = query_package.first()
            if not select_package:
                raise InvalidPackageIdError
            return select_package[0]

    async def list_packages(self, application_id: int, limit: int, offset: int):
        async with async_session() as session:
            query_packages = await session.execute(
                select(Package)
                .options(joinedload(Package.application))
                .filter(Package.application_id == application_id)
                .limit(limit)
                .offset(offset)
            )
            result_packages = query_packages.scalars().all()
            return result_packages


class UploadPackageRepo:
    async def upload_package(self, package_id: int, file: UploadFile = File(...)):
        upload_location = os.path.join(os.getcwd(), "Storage")
        upload_subdirectory = f"Package_{package_id}"
        upload_location = os.path.join(upload_location, upload_subdirectory)
        if not os.path.exists(upload_location):
            os.makedirs(upload_location)
        upload_string_name = file.filename
        file_location = os.path.join(upload_location, upload_string_name)
        async with aiofiles.open(file_location, "wb") as f:
            await f.write(await file.read())
        return file_location, upload_string_name

    async def get_size(self, file_location: str):
        stat_src = await aiofiles.os.stat(file_location)
        file_size = stat_src.st_size
        return file_size

    async def make_hash(self, file_location: str):
        async with aiofiles.open(file_location, "rb") as f:
            file_bytes = await f.read()
            file_hash = hashlib.sha256(file_bytes).hexdigest()
        return file_hash


class UpdatePackageRepo(UploadPackageRepo):
    async def update_package(
        self, application_id: int, package_id: int, file: UploadFile = File(...)
    ):
        async with async_session() as session:
            query_app = select(exists().where(Application.id == application_id))
            result_app = await session.execute(query_app)
            if not result_app.scalar():
                raise InvalidAppIdError
            query_package = await session.execute(
                select(Package)
                .options(joinedload(Package.application))
                .filter(
                    Package.id == package_id, Package.application_id == application_id
                )
            )
            select_package = query_package.first()
            if not select_package:
                raise InvalidPackageIdError
            upload_file = await self.upload_package(package_id, file)
            size = await self.get_size(upload_file[0])
            file_hash = await self.make_hash(upload_file[0])
            query_update = (
                update(Package)
                .where(
                    Package.id == package_id, Package.application_id == application_id
                )
                .values(
                    file=upload_file[1],
                    hash=file_hash,
                    size=size,
                    url=f"/v1/applications/{application_id}/packages/{package_id}/file",
                )
            )
            await session.execute(query_update)
            await session.commit()
            updated_result = await session.execute(
                select(Package)
                .options(joinedload(Package.application))
                .filter(
                    Package.id == package_id, Package.application_id == application_id
                )
            )
            updated_package = updated_result.first()
            return updated_package[0]


class DownloadPackageRepo(PackageRepo):
    async def download_package(self, application_id: int, package_id: int):
        get_pack = await self.get_package(application_id, package_id)
        file_name = get_pack.file
        file_location = os.path.join(
            os.getcwd(), f"Storage/Package_{package_id}/{file_name}"
        )
        if not os.path.exists(file_location):
            raise FileNotFoundError("File not found")
        return file_location, file_name
