import pytest

from updateservice.settings import setting

max_int = setting["POSTGRES_MAX_INT"]


@pytest.mark.asyncio
async def test_post_application_endpoint_201(
    http_client, application_obj, team_in_db, token_in_db
):
    post_data = {
        "name": application_obj.name,
        "description": application_obj.description,
    }
    response = await http_client.post(
        f"/v1/teams/{team_in_db.id}/applications",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=post_data,
    )
    data = response.json()
    assert data["name"] == application_obj.name
    assert data["description"] == application_obj.description
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_post_application_endpoint_400(
    http_client, team_in_db, application_in_db, token_in_db
):
    post_data = {
        "name": application_in_db.name,
        "description": application_in_db.description,
    }
    response = await http_client.post(
        f"/v1/teams/{team_in_db.id}/applications",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=post_data,
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "An application with the same name already exists"
    }


@pytest.mark.asyncio
async def test_post_application_endpoint_404(
    http_client, application_in_db, token_in_db
):
    post_data = {
        "name": application_in_db.name,
        "description": application_in_db.description,
    }
    invalid_id = -1
    response = await http_client.post(
        f"/v1/teams/{invalid_id}/applications",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=post_data,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The team with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_application_authentication_403(
    http_client, team_in_db, application_in_db
):
    response_create = await http_client.post(
        f"/v1/teams/{team_in_db.id}/applications",
    )
    response_list = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications"
    )
    response_patch = await http_client.patch(
        f"/v1/team/{application_in_db.team_id}/applications/{application_in_db.id}"
    )
    response_get_app = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications/{application_in_db.id}",
    )
    assert response_create.status_code == 403
    assert response_create.json() == {"detail": "Not authenticated"}
    assert response_list.status_code == 403
    assert response_list.json() == {"detail": "Not authenticated"}
    assert response_patch.status_code == 403
    assert response_patch.json() == {"detail": "Not authenticated"}
    assert response_get_app.status_code == 403
    assert response_get_app.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_application_authentication_401(
    http_client,
    team_in_db,
    application_in_db,
):
    invalid_token = "InvalidTokenString"
    response_create = await http_client.post(
        f"/v1/teams/{team_in_db.id}/applications",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_list = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_patch = await http_client.patch(
        f"/v1/team/{application_in_db.team_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_get_app = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response_create.status_code == 401
    assert response_create.json() == {"detail": "Token is not valid"}
    assert response_list.status_code == 401
    assert response_list.json() == {"detail": "Token is not valid"}
    assert response_patch.status_code == 401
    assert response_patch.json() == {"detail": "Token is not valid"}
    assert response_get_app.status_code == 401
    assert response_get_app.json() == {"detail": "Token is not valid"}


@pytest.mark.asyncio
async def test_list_applications_pagination_200(
    http_client, application_in_db, token_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=1&size={max_int}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0]["name"] == application_in_db.name
    assert data[0]["description"] == application_in_db.description


@pytest.mark.asyncio
async def test_list_applications_pagination_200_second_page(
    http_client, application_in_db, application_in_db_2, token_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=2&size=1",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert data[0]["name"] == application_in_db_2.name
    assert data[0]["description"] == application_in_db_2.description


@pytest.mark.asyncio
async def test_list_applications_pagination_422_page_ge(
    http_client, application_in_db, token_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=-7&size=20",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_ge"


@pytest.mark.asyncio
async def test_list_applications_pagination_422_page_le(
    http_client, application_in_db, token_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page={max_int+7}&size=20",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_le"


@pytest.mark.asyncio
async def test_list_applications_pagination_422_size_ge(
    http_client, application_in_db, token_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=1&size=-7",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_ge"


@pytest.mark.asyncio
async def test_list_applications_pagination_422_size_le(
    http_client, application_in_db, token_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=1&size={max_int+7}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_le"


@pytest.mark.asyncio
async def test_list_applications_pagination_404(
    http_client, application_in_db, token_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=7777&size=7777",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "This page has no items to display"}


@pytest.mark.asyncio
async def test_list_applications_pagination_400_offset(
    http_client, application_in_db, token_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page={max_int}&size={max_int}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Offset is too big"}


@pytest.mark.asyncio
async def test_list_get_application_list_404(http_client, token_in_db):
    invalid_id = -5
    response = await http_client.get(
        f"/v1/teams/{invalid_id}/applications?page=1&size={max_int}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": {
            "error": {"message": f"Team {invalid_id} does not exist", "code": 404}
        }
    }


@pytest.mark.asyncio
async def test_patch_application_200(
    http_client, token_in_db, application_in_db, update_application_obj
):
    update_data = {
        "name": update_application_obj.name,
        "description": update_application_obj.description,
    }
    response = await http_client.patch(
        f"/v1/team/{application_in_db.team_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=update_data,
    )
    data = response.json()
    assert data["name"] == update_application_obj.name
    assert data["description"] == update_application_obj.description
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_patch_application_400(
    http_client, token_in_db, application_in_db, application_in_db_2
):
    update_data = {
        "name": application_in_db_2.name,
        "description": application_in_db_2.description,
    }
    response = await http_client.patch(
        f"/v1/team/{application_in_db.team_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=update_data,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Application name already exists"}


@pytest.mark.asyncio
async def test_patch_application_404_team_id(
    http_client, token_in_db, application_in_db, application_in_db_2
):
    update_data = {
        "name": application_in_db_2.name,
        "description": application_in_db_2.description,
    }
    invalid_id = -5
    response = await http_client.patch(
        f"/v1/team/{invalid_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=update_data,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The team with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_patch_application_404_app_id(
    http_client, token_in_db, application_in_db, application_in_db_2
):
    update_data = {
        "name": application_in_db_2.name,
        "description": application_in_db_2.description,
    }
    invalid_id = -5
    response = await http_client.patch(
        f"/v1/team/{application_in_db.team_id}/applications/{invalid_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=update_data,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_get_application_details_200(http_client, token_in_db, application_in_db):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == application_in_db.id
    assert data["name"] == application_in_db.name
    assert data["description"] == application_in_db.description
    assert data["team"]["id"] == application_in_db.team_id


@pytest.mark.asyncio
async def test_get_application_details_404(http_client, token_in_db, application_in_db):
    invalid_id = -5
    response = await http_client.get(
        f"/v1/teams/{invalid_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The team with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_get_application_details_404(http_client, token_in_db, application_in_db):
    invalid_id = -5
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications/{invalid_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_search_application_200_case_insensitive(
    http_client, token_in_db, application_in_db
):
    search = application_in_db.name[:3]
    search_upper = search.upper()
    search_lower = search.lower()
    search_mix = search[0] + search[1].upper() + search[2]

    response_upper = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=1&size={max_int}&search={search_upper}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    response_lower = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=1&size={max_int}&search={search_lower}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    response_mix = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=1&size={max_int}&search={search_mix}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response_upper.status_code == 200
    assert response_upper.json()[0]["name"] == application_in_db.name
    assert response_lower.status_code == 200
    assert response_lower.json()[0]["name"] == application_in_db.name
    assert response_mix.status_code == 200
    assert response_mix.json()[0]["name"] == application_in_db.name


@pytest.mark.asyncio
async def test_search_application_404(http_client, token_in_db, application_in_db):
    search = 777
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications?page=1&size={max_int}&search={search}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": f"No applications found for '{search}'"}


@pytest.mark.asyncio
async def test_get_application_200_not_assigned(
    http_client, token_in_db, application_in_db, group_in_db
):
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == application_in_db.name
    assert data["description"] == application_in_db.description
    assert data["team"]["id"] == application_in_db.team_id
    assert isinstance(data["group"], list)


@pytest.mark.asyncio
async def test_get_application_200_assigned(
    http_client, token_in_db, application_in_db, group_in_db
):

    response_post = await http_client.post(
        f"/v1/applications/{application_in_db.id}/groups/{group_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data_post = response_post.json()
    assert response_post.status_code == 201
    assert data_post["application_id"] == application_in_db.id
    assert data_post["group_id"] == group_in_db.id

    response_get = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data_get = response_get.json()
    assert response_get.status_code == 200
    assert data_get["name"] == application_in_db.name
    assert data_get["description"] == application_in_db.description
    assert data_get["team"]["id"] == application_in_db.team_id
    assert isinstance(data_get["group"], list)
    assert data_get["group"][0] == group_in_db.id


@pytest.mark.asyncio
async def test_get_application_404_team_id(http_client, token_in_db, application_in_db):
    invalid_id = -7
    response = await http_client.get(
        f"/v1/teams/{-7}/applications/{application_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The team with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_get_application_404_app_id(http_client, token_in_db, application_in_db):
    invalid_id = -7
    response = await http_client.get(
        f"/v1/teams/{application_in_db.team_id}/applications/{invalid_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }
