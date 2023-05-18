import pytest


@pytest.mark.asyncio
async def test_post_token_endpoint_201(http_client, user_in_db):
    response = await http_client.post(
        f"/internal/v1/users/{user_in_db.id}/token",
        headers={"accept": "application/json"},
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_post_token_endpoint_404(
    http_client,
    token_in_db,
):
    invalid_id = -5
    response = await http_client.post(
        f"/internal/v1/users/{invalid_id}/token", headers={"accept": "application/json"}
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The user with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_delete_token_endpoint_200(http_client, token_in_db):

    response = await http_client.delete(
        f"/internal/v1/users/{token_in_db.user_id}/token/{token_in_db.token}",
        headers={"accept": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == "The token has been deleted successfully"


@pytest.mark.asyncio
async def test_delete_token_endpoint_invalid_user_id_404(http_client, token_in_db):
    invalid_id = -5
    response = await http_client.delete(
        f"/internal/v1/users/{invalid_id}/token/{token_in_db.token}",
        headers={"accept": "application/json"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The user with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_delete_token_endpoint_invalid_token_404(http_client, token_in_db):
    invalid_token = "IvalidToken"
    response = await http_client.delete(
        f"/internal/v1/users/{token_in_db.user_id}/token/{invalid_token}",
        headers={"accept": "application/json"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Could not find this token for the requested user"
    }
