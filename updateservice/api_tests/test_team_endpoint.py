import pytest

from updateservice.settings import setting

max_int = setting["POSTGRES_MAX_INT"]


@pytest.mark.asyncio
async def test_post_team_endpoint_201(http_client, team_obj):
    post_data = {
        "name": team_obj.name,
        "description": team_obj.description,
    }
    response = await http_client.post(
        "/internal/v1/teams", headers={"accept": "application/json"}, json=post_data
    )
    data = response.json()
    assert data["name"] == team_obj.name
    assert data["description"] == team_obj.description
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_post_team_endpoint_400(http_client, team_in_db):
    post_data = {
        "name": team_in_db.name,
        "description": team_in_db.description,
    }
    response = await http_client.post(
        "/internal/v1/teams", headers={"accept": "application/json"}, json=post_data
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "This team already exists"}


@pytest.mark.asyncio
async def test_teams_list_pagination_200(http_client, team_in_db):

    response = await http_client.get(f"/internal/v1/teams?page=1&size=20")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == team_in_db.name
    assert data[0]["description"] == team_in_db.description


@pytest.mark.asyncio
async def test_teams_list_pagination_422_page_ge(http_client):

    response = await http_client.get(f"/internal/v1/teams?page=-7&size=20")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_ge"


@pytest.mark.asyncio
async def test_teams_list_pagination_422_page_le(http_client):

    response = await http_client.get(f"/internal/v1/teams?page={max_int+7}&size=1")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_le"


@pytest.mark.asyncio
async def test_teams_list_pagination_422_size_ge(http_client):

    response = await http_client.get(f"/internal/v1/teams?page=1&size=-7")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_ge"


@pytest.mark.asyncio
async def test_teams_list_pagination_422_size_le(http_client):

    response = await http_client.get(f"/internal/v1/teams?page=1&size={max_int+7}")
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_le"


@pytest.mark.asyncio
async def test_teams_list_pagination_404(http_client):

    response = await http_client.get(f"/internal/v1/teams?page=7777&size=7777")
    assert response.status_code == 404
    assert response.json() == {"detail": "This page has no items to display"}


@pytest.mark.asyncio
async def test_teams_list_pagination_400_offset(http_client):

    response = await http_client.get(
        f"/internal/v1/teams?page={max_int}&size={max_int}"
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Offset is too big"}


@pytest.mark.asyncio
async def test_teams_list_pagination_200_second_page(
    http_client, team_in_db, team_in_db_2
):

    response = await http_client.get(f"/internal/v1/teams?page=2&size=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == team_in_db_2.name
    assert data[0]["description"] == team_in_db_2.description


@pytest.mark.asyncio
async def test_update_a_team_200(http_client, team_in_db, update_team_obj):

    update_team_data = {
        "name": update_team_obj.name,
        "description": update_team_obj.description,
    }

    response = await http_client.put(
        f"/internal/v1/teams/{team_in_db.id}",
        headers={"accept": "application/json"},
        json=update_team_data,
    )
    assert response.json()["name"] == update_team_obj.name
    assert response.json()["description"] == update_team_obj.description

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_a_team_400(http_client, team_in_db, team_in_db_2):

    update_team_data = {
        "name": team_in_db_2.name,
        "description": team_in_db_2.description,
    }

    response = await http_client.put(
        f"/internal/v1/teams/{team_in_db.id}",
        headers={"accept": "application/json"},
        json=update_team_data,
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Team name already exists"}

    assert team_in_db.name != team_in_db_2.name
