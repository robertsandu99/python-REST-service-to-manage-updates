import datetime
from datetime import timedelta

import jwt
from sqlalchemy import and_, select, update
from sqlalchemy.orm import joinedload

from updateservice.connection_db import async_session
from updateservice.models.token import Token
from updateservice.models.user_teams import User
from updateservice.settings import setting
from updateservice.utils.exceptions import (
    InvalidUserIdError,
    TokenDeletedError,
    UserTokenNotFound,
)

jwt_secret = setting["secret_key"]


class TokenRepo:
    async def create_token(self, user_id: int):
        async with async_session() as session:
            query = await session.execute(select(User).filter(User.id == user_id))
            check_user_id = query.first()
            if check_user_id is None:
                raise InvalidUserIdError
            exp = datetime.datetime.utcnow() + timedelta(seconds=43200)
            payload = {"user_id": user_id, "exp": exp}
            encoded_jwt = jwt.encode(payload, jwt_secret, algorithm="HS256")
            created_token = Token(user_id=user_id, token=encoded_jwt)

            session.add(created_token)
            await session.commit()
            await session.refresh(created_token)

            return created_token


class DeleteTokenRepo:
    async def delete_token(self, user_id: int, token: str):
        async with async_session() as session:
            user_query = await session.execute(select(User).filter(User.id == user_id))
            check_user_id = user_query.first()
            if check_user_id is None:
                raise InvalidUserIdError
            query_token_user = await session.execute(
                select(Token)
                .options(joinedload(Token.user_relationship))
                .filter(Token.user_id == user_id, Token.token == token)
            )
            selected_token = query_token_user.first()
            if not selected_token:
                raise UserTokenNotFound
            delete_query = (
                update(Token)
                .values(deleted=True)
                .filter(and_(Token.user_id == user_id, Token.token == token))
            )
            await session.execute(delete_query)
            await session.commit()

            return "The token has been deleted successfully"


class CheckTokenRepo:
    async def token_status(self, user_id: int, token: str, deleted: bool):
        async with async_session() as session:
            token_query = await session.execute(
                select(Token.user_id, Token.token, Token.deleted).filter(
                    Token.user_id == user_id,
                    Token.token == token,
                    Token.deleted == deleted,
                )
            )
        the_token = token_query.first()
        if the_token is None:
            raise TokenDeletedError
        return the_token
