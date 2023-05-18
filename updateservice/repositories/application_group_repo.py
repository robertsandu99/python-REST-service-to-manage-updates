from sqlalchemy import delete, select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import exists

from updateservice.connection_db import async_session
from updateservice.models.application import Application
from updateservice.models.application_group import ApplicationGroup, Group
from updateservice.models.schema_application_group import GroupCreate
from updateservice.utils.exceptions import (
    AlreadyAssignedError,
    ApplicationAssignedError,
    InvalidAppIdError,
    InvalidGroupIdError,
    NotAssignedError,
)


class GroupRepo:
    async def create_group(self, group: GroupCreate):
        async with async_session() as session:
            new_group = Group(name=group.name)
            session.add(new_group)
            await session.commit()
            await session.refresh(new_group)
            return new_group

    async def delete_group(self, group_id: int):
        async with async_session() as session:
            query_group = select(exists().where(Group.id == group_id))
            query_app_group = select(
                exists().where(
                    ApplicationGroup.group_id == group_id,
                )
            )
            result_group = await session.execute(query_group)
            result_app_group = await session.execute(query_app_group)
            if not result_group.scalar():
                raise InvalidGroupIdError
            elif result_app_group.scalar():
                raise ApplicationAssignedError()
            delete_group = delete(Group).filter(Group.id == group_id)
            await session.execute(delete_group)
            await session.commit()
            return "Group has been deleted"


class ApplicationGroupRepo:
    async def check_application_group(self, application_id: int, group_id: int):
        async with async_session() as session:
            query_app_group = select(
                exists().where(
                    ApplicationGroup.application_id == application_id,
                    ApplicationGroup.group_id == group_id,
                )
            )
            result_app_group = await session.execute(query_app_group)
            if not result_app_group.scalar():
                raise AlreadyAssignedError(application_id, group_id)
            return True

    async def create_application_group(self, application_id: int, group_id: int):
        async with async_session() as session:
            query_app = select(exists().where(Application.id == application_id))
            query_group = select(exists().where(Group.id == group_id))
            query_app_group = select(
                exists().where(
                    ApplicationGroup.application_id == application_id,
                    ApplicationGroup.group_id == group_id,
                )
            )
            result_app = await session.execute(query_app)
            result_group = await session.execute(query_group)
            result_app_group = await session.execute(query_app_group)
            if not result_app.scalar():
                raise InvalidAppIdError
            elif not result_group.scalar():
                raise InvalidGroupIdError
            elif result_app_group.scalar():
                raise AlreadyAssignedError(application_id, group_id)
            new_application_group = ApplicationGroup(
                application_id=application_id, group_id=group_id
            )
            session.add(new_application_group)
            await session.commit()
            select_application_group = await session.execute(
                select(ApplicationGroup).filter(
                    ApplicationGroup.application_id == application_id,
                    ApplicationGroup.group_id == group_id,
                )
            )
            select_object = select_application_group.first()
            application_group = dict(select_object).get("ApplicationGroup")
            return application_group

    async def unassign_application(self, application_id: int, group_id: int):
        async with async_session() as session:
            query_app = select(exists().where(Application.id == application_id))
            query_group = select(exists().where(Group.id == group_id))
            query_app_group = select(
                exists().where(
                    ApplicationGroup.application_id == application_id,
                    ApplicationGroup.group_id == group_id,
                )
            )
            result_app = await session.execute(query_app)
            result_group = await session.execute(query_group)
            result_app_group = await session.execute(query_app_group)
            if not result_app.scalar():
                raise InvalidAppIdError
            elif not result_group.scalar():
                raise InvalidGroupIdError
            elif not result_app_group.scalar():
                raise NotAssignedError(application_id, group_id)
            delete_app_group = delete(ApplicationGroup).filter(
                ApplicationGroup.application_id == application_id,
                ApplicationGroup.group_id == group_id,
            )
            await session.execute(delete_app_group)
            await session.commit()
            return "Application has been unassigned"
