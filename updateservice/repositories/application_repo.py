from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.expression import exists

from updateservice.connection_db import async_session
from updateservice.models.application import Application
from updateservice.models.application_group import ApplicationGroup
from updateservice.models.schema_application import (
    ApplicationCreate,
    ApplicationPatch,
    GroupIdSchema,
)
from updateservice.models.user_teams import Team
from updateservice.utils.exceptions import (
    ApplicationNotFoundError,
    InvalidAppIdError,
    InvalidTeamIdError,
    TeamIdError,
)


class ApplicationRepo:
    async def check_app_exists(self, application_id: int):

        async with async_session() as session:
            query = select(exists().where(Application.id == application_id))
            result_id = await session.execute(query)
            if not result_id.scalar():
                raise InvalidAppIdError
            return True

    async def create_application(self, team_id: int, app: ApplicationCreate):

        async with async_session() as session:
            query = select(exists().where(Team.id == team_id))
            result_team = await session.execute(query)
            if not result_team.scalar():
                raise InvalidTeamIdError
            else:
                new_app = Application(
                    team_id=team_id, name=app.name, description=app.description
                )
                session.add(new_app)
                await session.commit()
                select_app = await session.execute(
                    select(Application)
                    .options(joinedload(Application.team))
                    .filter(
                        Application.team_id == team_id, Application.name == app.name
                    )
                )
                select_the_app = select_app.first()
                the_app = dict(select_the_app).get("Application")
                return the_app

    async def get_applications_list(
        self, team_id: int, limit: int, offset: int, search: str
    ):

        async with async_session() as session:
            query = select(exists().where(Team.id == team_id))
            result_team = await session.execute(query)
            if not result_team.scalar():
                raise TeamIdError(team_id)
            if search:
                select_apps = await session.execute(
                    select(Application)
                    .options(joinedload(Application.team))
                    .filter(
                        Application.team_id == team_id,
                        Application.name.ilike(f"%{search}%"),
                    )
                    .limit(limit)
                    .offset(offset)
                )
            else:
                select_apps = await session.execute(
                    select(Application)
                    .options(joinedload(Application.team))
                    .filter(Application.team_id == team_id)
                    .limit(limit)
                    .offset(offset)
                )
            apps_list = select_apps.scalars().all()
            if search and not apps_list:
                raise ApplicationNotFoundError(search)
            return apps_list

    async def patch_application(
        self, team_id: int, application_id: int, app: ApplicationPatch
    ):

        async with async_session() as session:
            query_team = select(exists().where(Team.id == team_id))
            result_team = await session.execute(query_team)
            if not result_team.scalar():
                raise InvalidTeamIdError
            query_app = await session.execute(
                select(Application).filter(
                    Application.id == application_id, Application.team_id == team_id
                )
            )
            result = query_app.first()
            if not result:
                raise InvalidAppIdError
            updated_application = (
                update(Application)
                .where(Application.id == application_id)
                .values(**app.dict(exclude_unset=True))
            )
            await session.execute(updated_application)
            await session.commit()
            updated_result = await session.execute(
                select(Application)
                .options(joinedload(Application.team))
                .filter(Application.id == application_id)
            )
            application_updated = updated_result.first()
            return application_updated[0]

    async def get_app(self, team_id: int, application_id: int):
        async with async_session() as session:
            query_team = select(exists().where(Team.id == team_id))
            result_team = await session.execute(query_team)
            if not result_team.scalar():
                raise InvalidTeamIdError
            query_app = await session.execute(
                select(Application)
                .options(joinedload(Application.team), joinedload(Application.groups))
                .filter(
                    Application.team_id == team_id, Application.id == application_id
                )
            )
            selected_app = query_app.first()
            if not selected_app:
                raise InvalidAppIdError
            group_ids = [groups_ids.id for groups_ids in selected_app[0].groups]
            return selected_app[0], group_ids
