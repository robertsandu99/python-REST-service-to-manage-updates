import datetime

from sqlalchemy import select, update

from updateservice.connection_db import async_session
from updateservice.models.schema import UserCreate
from updateservice.models.user_teams import User
from updateservice.utils.exceptions import UsersNotFoundError


class UserRepo:
    async def create_user(self, user: UserCreate):
        async with async_session() as session:
            new_user = User(email=user.email, full_name=user.full_name)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user

    async def get_list_users(self, limit: int, offset: int, search: str):
        async with async_session() as session:
            if search:
                select_users = await session.execute(
                    select(User)
                    .filter(User.full_name.ilike(f"%{search}%"))
                    .limit(limit)
                    .offset(offset)
                )
            else:
                select_users = await session.execute(
                    select(User).limit(limit).offset(offset)
                )
            selected_users = select_users.scalars().all()
            if search and not selected_users:
                raise UsersNotFoundError(search)
            return selected_users


class UserLoginRepo:
    async def update_last_login(self, user_id: int):
        async with async_session() as session:

            update_query = (
                update(User)
                .where(User.id == user_id)
                .values(last_login=datetime.datetime.utcnow())
            )
            await session.execute(update_query)
            await session.commit()
