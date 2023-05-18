from fastapi import APIRouter, Depends, HTTPException, status

from updateservice.models.schema_tokens import TokenBase, TokenPayload
from updateservice.repositories.tokens_repo import DeleteTokenRepo, TokenRepo
from updateservice.utils.exceptions import InvalidIdError, UserTokenNotFound

router = APIRouter()


@router.post(
    "/internal/v1/users/{user_id}/token",
    response_model=TokenBase,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_token(
    user_id: int,
    db_session: TokenRepo = Depends(TokenRepo),
):
    try:

        new_user_token = await db_session.create_token(user_id)

    except InvalidIdError as iie:

        raise HTTPException(status_code=404, detail=iie.message)

    token_response = TokenBase(
        id=new_user_token.id,
        token=TokenPayload(user_id=new_user_token.user_id, token=new_user_token.token),
    )
    return token_response


@router.delete(
    "/internal/v1/users/{user_id}/token/{token}",
    status_code=status.HTTP_200_OK,
)
async def delete_user_token(
    user_id: int, token: str, db_session: DeleteTokenRepo = Depends(DeleteTokenRepo)
):
    try:
        delete_the_token = await db_session.delete_token(user_id, token)
    except InvalidIdError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except UserTokenNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    return delete_the_token
