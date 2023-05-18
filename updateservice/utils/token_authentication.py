import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError

from updateservice.repositories.tokens_repo import CheckTokenRepo
from updateservice.repositories.user_repo import UserLoginRepo
from updateservice.settings import setting
from updateservice.utils.exceptions import TokenDeletedError

jwt_secret = setting["secret_key"]


class UpdateUserLogin(UserLoginRepo):
    def __init__(self, db_session: UserLoginRepo = Depends(UserLoginRepo)):
        self.db_session = db_session

    async def update_user_last_login(self, user_id: int):
        try:
            user_last_login = await self.db_session.update_last_login(user_id)
        finally:
            return user_last_login


class CheckTokenStatus(CheckTokenRepo):
    def __init__(self, db_session: CheckTokenRepo = Depends(CheckTokenRepo)):
        self.db_session = db_session

    async def check_if_token_is_deleted(self, user_id: int, token: str, deleted: bool):
        try:
            status = await self.db_session.token_status(user_id, token, deleted)
            if status.deleted != deleted:
                return False
            return True
        except TokenDeletedError as e:
            raise HTTPException(status_code=401, detail=e.message)


async def check_token_authentication(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    user: UpdateUserLogin = Depends(UpdateUserLogin),
    check: CheckTokenStatus = Depends(CheckTokenStatus),
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token is not valid",
    )

    encoded_token = credentials.credentials

    try:
        decoded_token = jwt.decode(encoded_token, jwt_secret, algorithms="HS256")
        if decoded_token is None:
            raise credentials_exception
        user_id = decoded_token["user_id"]
        token = encoded_token
        deleted = False
        check_status = await check.check_if_token_is_deleted(user_id, token, deleted)
        if not check_status:
            raise credentials_exception
        await user.update_user_last_login(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except PyJWTError:
        raise credentials_exception
