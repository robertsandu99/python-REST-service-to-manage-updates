import pytest

from updateservice.settings import setting

max_int = setting["POSTGRES_MAX_INT"]


@pytest.mark.asyncio
async def test_post_user_endpoint_201(http_client, user_obj):
    post_data = {
        "email": user_obj.email,
        "full_name": user_obj.full_name,
    }
    response = await http_client.post(
        "/internal/v1/users", headers={"accept": "application/json"}, json=post_data
    )
    data = response.json()
    assert data["email"] == user_obj.email
    assert data["full_name"] == user_obj.full_name
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_post_user_endpoint_400(http_client, user_in_db):
    post_data = {
        "email": user_in_db.email,
        "full_name": user_in_db.full_name,
    }
    response = await http_client.post(
        "/internal/v1/users", headers={"accept": "application/json"}, json=post_data
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "There is already a user registered with this email"
    }


@pytest.mark.asyncio
async def test_users_list_pagination_200(http_client, user_in_db):

    response = await http_client.get(f"/internal/v1/users?page=1&size=20")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["full_name"] == user_in_db.full_name


@pytest.mark.asyncio
async def test_users_list_pagination_422_page_ge(http_client):

    response = await http_client.get(f"/internal/v1/users?page=-7&size=20")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_ge"


@pytest.mark.asyncio
async def test_users_list_pagination_422_page_le(http_client):

    response = await http_client.get(f"/internal/v1/users?page={max_int+7}&size=1")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_le"


@pytest.mark.asyncio
async def test_users_list_pagination_422_size_ge(http_client):

    response = await http_client.get(f"/internal/v1/users?page=1&size=-7")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_ge"


@pytest.mark.asyncio
async def test_users_list_pagination_422_size_le(http_client):

    response = await http_client.get(f"/internal/v1/users?page=1&size={max_int+7}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_le"


@pytest.mark.asyncio
async def test_users_list_pagination_404(http_client):

    response = await http_client.get(f"/internal/v1/users?page=7777&size=7777")
    assert response.status_code == 404
    assert response.json() == {"detail": "This page has no items to display"}


@pytest.mark.asyncio
async def test_users_list_pagination_400_offset(http_client):

    response = await http_client.get(
        f"/internal/v1/users?page={max_int}&size={max_int}"
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Offset is too big"}


@pytest.mark.asyncio
async def test_users_list_pagination_200_second_page(
    http_client, user_in_db, user_in_db_2
):

    response = await http_client.get(f"/internal/v1/users?page=2&size=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["full_name"] == user_in_db_2.full_name


@pytest.mark.asyncio
async def test_search_user_200_case_insensitive(http_client, user_in_db):

    search = user_in_db.full_name[:3]
    search_upper = search.upper()
    search_lower = search.lower()
    search_mix = search[0] + search[1].upper() + search[2]

    response_upper = await http_client.get(
        f"/internal/v1/users?page=1&size=20&search={search_upper}",
    )
    response_lower = await http_client.get(
        f"/internal/v1/users?page=1&size=20&search={search_lower}",
    )
    response_mix = await http_client.get(
        f"/internal/v1/users?page=1&size=20&search={search_mix}",
    )
    assert response_upper.status_code == 200
    assert response_upper.json()[0]["full_name"] == user_in_db.full_name
    assert response_lower.status_code == 200
    assert response_lower.json()[0]["full_name"] == user_in_db.full_name
    assert response_mix.status_code == 200
    assert response_mix.json()[0]["full_name"] == user_in_db.full_name


@pytest.mark.asyncio
async def test_search_user_404(http_client, user_in_db):
    search = 777
    response = await http_client.get(
        f"/internal/v1/users?page=1&size={max_int}&search={search}",
    )
    assert response.status_code == 404
    assert response.json() == {"detail": f"No users found for '{search}'"}
