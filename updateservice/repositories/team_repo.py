from fastapi import HTTPException, status
from sqlalchemy import func, update
from sqlalchemy.future import select

from updateservice.connection_db import async_session
from updateservice.models.schema import TeamCreate, TeamUpdate
from updateservice.models.user_teams import Team


class TeamRepo:
    async def create_team(self, team: TeamCreate):
        async with async_session() as session:
            new_team = Team(name=team.name, description=team.description)
            session.add(new_team)
            await session.commit()
            await session.refresh(new_team)
            return new_team


class GetTeamRepo:
    async def get_all_teams(self, limit: int, offset: int):
        async with async_session() as session:
            select_teams = await session.execute(
                select(Team).limit(limit).offset(offset)
            )
            return select_teams.scalars().all()


class PutTeamRepo:
    async def update_team(self, team_id: int, team: TeamUpdate):
        async with async_session() as session:
            update_post_query = await session.execute(
                select(Team).filter(Team.id == team_id)
            )

            post = update_post_query.first()
            if post == None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"The team with id:{team_id} does not exists",
                )

            updated_query = (
                update(Team)
                .filter(Team.id == team_id)
                .where(Team.id == team_id)
                .values(team.dict())
            )
            updated_query.name = team.name
            updated_query.description = team.description

            await session.execute(updated_query)
            await session.commit()
            updated_post_query = await session.execute(
                select(
                    Team.id,
                    Team.name,
                    Team.description,
                    Team.created_at,
                    Team.updated_at,
                ).filter(Team.id == team_id)
            )
            updated_post = updated_post_query.first()
            return updated_post
