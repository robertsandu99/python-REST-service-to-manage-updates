import pytest

from updateservice.settings import setting

max_str = setting["POSTGRES_MAX_STR"]

invalid_id = -7


@pytest.mark.asyncio
async def test_group_authentication_403(http_client, group_in_db):
    response_create = await http_client.post(f"/v1/groups")
    response_delete = await http_client.delete(f"/v1/groups/{group_in_db.id}")
    assert response_create.status_code == 403
    assert response_create.json() == {"detail": "Not authenticated"}
    assert response_delete.status_code == 403
    assert response_delete.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_group_authentication_401(http_client, group_in_db):
    invalid_token = "InvalidTokenString"
    response_create = await http_client.post(
        f"/v1/groups",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_delete = await http_client.delete(
        f"/v1/groups/{group_in_db.id}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response_create.status_code == 401
    assert response_create.json() == {"detail": "Token is not valid"}
    assert response_delete.status_code == 401
    assert response_delete.json() == {"detail": "Token is not valid"}


@pytest.mark.asyncio
async def test_application_group_authentication_403(
    http_client, group_in_db, application_in_db, application_group_in_db
):
    response_create = await http_client.post(
        f"/v1/applications/{application_in_db.id}/groups/{group_in_db.id}"
    )
    response_delete = await http_client.delete(
        f"/v1/applications/{application_group_in_db.application_id}/groups/{application_group_in_db.group_id}",
    )
    assert response_create.status_code == 403
    assert response_create.json() == {"detail": "Not authenticated"}
    assert response_delete.status_code == 403
    assert response_delete.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_application_group_authentication_401(
    http_client, group_in_db, application_in_db, application_group_in_db
):
    invalid_token = "InvalidTokenString"
    response_create = await http_client.post(
        f"/v1/applications/{application_in_db.id}/groups/{group_in_db.id}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_delete = await http_client.delete(
        f"/v1/applications/{application_group_in_db.application_id}/groups/{application_group_in_db.group_id}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response_create.status_code == 401
    assert response_create.json() == {"detail": "Token is not valid"}
    assert response_delete.status_code == 401
    assert response_delete.json() == {"detail": "Token is not valid"}


@pytest.mark.asyncio
async def test_post_group_endpoint_201(http_client, group_obj, token_in_db):
    post_data = {"name": group_obj.name}
    response = await http_client.post(
        f"/v1/groups",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=post_data,
    )
    assert response.status_code == 201
    assert response.json()["name"] == group_obj.name


@pytest.mark.asyncio
async def test_post_group_endpoint_422(http_client, group_obj, token_in_db):
    post_data = {"name": max_str}
    response = await http_client.post(
        f"/v1/groups",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=post_data,
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.any_str.max_length"


@pytest.mark.asyncio
async def test_post_group_endpoint_400(http_client, group_in_db, token_in_db):
    post_data = {"name": group_in_db.name}
    response = await http_client.post(
        f"/v1/groups",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=post_data,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "A group with the same name already exists"}


@pytest.mark.asyncio
async def test_delete_group_endpoint_200(http_client, group_in_db_2, token_in_db):
    response = await http_client.delete(
        f"/v1/groups/{group_in_db_2.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 200
    assert response.json() == "Group has been deleted"


@pytest.mark.asyncio
async def test_delete_group_endpoint_404(http_client, token_in_db):
    response = await http_client.delete(
        f"/v1/groups/{invalid_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The group with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_delete_group_endpoint_400(
    http_client, token_in_db, application_group_in_db
):
    response = await http_client.delete(
        f"/v1/groups/{application_group_in_db.group_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Can not delete groups with apllications assigned to it"
    }


@pytest.mark.asyncio
async def test_application_group_endpoint_201(
    http_client, group_in_db, application_in_db, token_in_db
):
    response = await http_client.post(
        f"/v1/applications/{application_in_db.id}/groups/{group_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert response.status_code == 201
    assert data["application_id"] == application_in_db.id
    assert data["group_id"] == group_in_db.id


@pytest.mark.asyncio
async def test_application_group_endpoint_404_app_id(
    http_client, group_in_db, application_in_db, token_in_db
):
    response = await http_client.post(
        f"/v1/applications/{invalid_id}/groups/{group_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert response.status_code == 404
    assert data == {"detail": "The application with the id requested does not exist"}


@pytest.mark.asyncio
async def test_application_group_endpoint_404_group_id(
    http_client, group_in_db, application_in_db, token_in_db
):
    response = await http_client.post(
        f"/v1/applications/{application_in_db.id}/groups/{invalid_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert response.status_code == 404
    assert data == {"detail": "The group with the id requested does not exist"}


@pytest.mark.asyncio
async def test_application_group_endpoint_400(
    http_client, group_in_db, application_in_db, token_in_db
):
    response_assign = await http_client.post(
        f"/v1/applications/{application_in_db.id}/groups/{group_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response_assign.json()
    assert response_assign.status_code == 201
    assert data["application_id"] == application_in_db.id
    assert data["group_id"] == group_in_db.id

    response_reassign = await http_client.post(
        f"/v1/applications/{application_in_db.id}/groups/{group_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response_reassign.status_code == 400
    assert response_reassign.json() == {
        "detail": f"Application {application_in_db.id} already assign to group {group_in_db.id}"
    }


@pytest.mark.asyncio
async def test_delete_application_group_endpoint_200(
    http_client, application_group_in_db_2, token_in_db
):
    response = await http_client.delete(
        f"/v1/applications/{application_group_in_db_2.application_id}/groups/{application_group_in_db_2.group_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )

    assert response.status_code == 200
    assert response.json() == "Application has been unassigned"


@pytest.mark.asyncio
async def test_delete_application_group_endpoint_404_app_id(
    http_client, application_group_in_db_2, token_in_db
):
    response = await http_client.delete(
        f"/v1/applications/{invalid_id}/groups/{application_group_in_db_2.group_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_delete_application_group_endpoint_404_group_id(
    http_client, application_group_in_db_2, token_in_db
):
    response = await http_client.delete(
        f"/v1/applications/{application_group_in_db_2.application_id}/groups/{invalid_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "The group with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_delete_application_group_endpoint_404_not_assigned(
    http_client, application_in_db, group_in_db, token_in_db
):
    response = await http_client.delete(
        f"/v1/applications/{application_in_db.id}/groups/{group_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": f"Application {application_in_db.id} not assigned to group {group_in_db.id}"
    }
