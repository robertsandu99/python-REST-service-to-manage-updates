import aiofiles
import pytest

from updateservice.settings import setting

max_int = setting["POSTGRES_MAX_INT"]


@pytest.mark.asyncio
async def test_package_authentication_403(
    http_client, application_in_db, package_in_db
):
    response_create = await http_client.post(
        f"/v1/applications/{application_in_db.id}/packages"
    )
    response_delete = await http_client.delete(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}"
    )
    response_get = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}",
    )
    response_list = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages",
    )
    response_upload = await http_client.post(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file"
    )
    response_download = await http_client.post(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file"
    )
    response_download = await http_client.post(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file"
    )
    assert response_create.status_code == 403
    assert response_create.json() == {"detail": "Not authenticated"}
    assert response_delete.status_code == 403
    assert response_delete.json() == {"detail": "Not authenticated"}
    assert response_get.status_code == 403
    assert response_get.json() == {"detail": "Not authenticated"}
    assert response_list.status_code == 403
    assert response_list.json() == {"detail": "Not authenticated"}
    assert response_upload.status_code == 403
    assert response_upload.json() == {"detail": "Not authenticated"}
    assert response_download.status_code == 403
    assert response_download.json() == {"detail": "Not authenticated"}
    assert response_download.status_code == 403
    assert response_download.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_package_authentication_401(
    http_client, application_in_db, package_in_db
):
    invalid_token = "InvalidTokenString"
    response_create = await http_client.post(
        f"/v1/applications/{application_in_db.id}/packages",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_delete = await http_client.delete(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_get = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_list = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_upload = await http_client.post(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_download = await http_client.post(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    response_download = await http_client.post(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )

    assert response_create.status_code == 401
    assert response_create.json() == {"detail": "Token is not valid"}
    assert response_delete.status_code == 401
    assert response_delete.json() == {"detail": "Token is not valid"}
    assert response_get.status_code == 401
    assert response_get.json() == {"detail": "Token is not valid"}
    assert response_list.status_code == 401
    assert response_list.json() == {"detail": "Token is not valid"}
    assert response_upload.status_code == 401
    assert response_upload.json() == {"detail": "Token is not valid"}
    assert response_download.status_code == 401
    assert response_download.json() == {"detail": "Token is not valid"}
    assert response_download.status_code == 401
    assert response_download.json() == {"detail": "Token is not valid"}


@pytest.mark.asyncio
async def test_post_package_endpoint_201(
    http_client, application_in_db, package_obj, token_in_db
):
    post_data = {
        "version": package_obj.version,
        "description": package_obj.description,
    }
    response = await http_client.post(
        f"/v1/applications/{application_in_db.id}/packages",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=post_data,
    )
    data = response.json()
    assert data["version"] == package_obj.version
    assert data["description"] == package_obj.description
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_post_package_endpoint_404(http_client, package_in_db, token_in_db):
    post_data = {
        "version": package_in_db.version,
        "description": package_in_db.description,
    }
    invalid_id = -7
    response = await http_client.post(
        f"/v1/applications/{invalid_id}/packages",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        json=post_data,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_delete_package_200(http_client, token_in_db, package_in_db):
    response = await http_client.delete(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )

    assert response.status_code == 200
    assert response.json() == "Package has been successfully deleted"


@pytest.mark.asyncio
async def test_delete_package_invalid_app_id_404(
    http_client, package_in_db, token_in_db
):
    invalid_id = -7
    response = await http_client.delete(
        f"/v1/applications/{invalid_id}/packages/{package_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_delete_package_invalid_pack_id_404(
    http_client, package_in_db, token_in_db
):
    invalid_id = -7
    response = await http_client.delete(
        f"/v1/applications/{package_in_db.application_id}/packages/{invalid_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The package with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_get_package_200(http_client, package_in_db, token_in_db):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == package_in_db.id
    assert data["application"]["id"] == package_in_db.application_id
    assert data["version"] == package_in_db.version
    assert data["description"] == package_in_db.description


@pytest.mark.asyncio
async def test_get_package_invalid_app_id_404(http_client, package_in_db, token_in_db):
    invalid_id = -7
    response = await http_client.get(
        f"/v1/applications/{invalid_id}/packages/{package_in_db.id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_get_package_invalid_pack_id_404(http_client, package_in_db, token_in_db):
    invalid_id = -7
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages/{invalid_id}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The package with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_get_packages_list_404(http_client, token_in_db):
    invalid_id = -7
    response = await http_client.get(
        f"/v1/applications/{invalid_id}/packages?page=1&size={max_int}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_package_pagination_200(http_client, package_in_db, token_in_db):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages?page=1&size={max_int}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert isinstance(data, list)
    assert response.status_code == 200
    assert data[0]["version"] == package_in_db.version
    assert data[0]["description"] == package_in_db.description


@pytest.mark.asyncio
async def test_package_pagination_200_second_page(
    http_client, package_in_db, package_in_db_2, token_in_db
):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages?page=2&size=1",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response.json()
    assert isinstance(data, list)
    assert response.status_code == 200
    assert data[0]["version"] == package_in_db_2.version
    assert data[0]["description"] == package_in_db_2.description


@pytest.mark.asyncio
async def test_package_pagination_422_page_ge(http_client, package_in_db, token_in_db):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages?page=-7&size=20",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_ge"


@pytest.mark.asyncio
async def test_package_pagination_422_page_le(http_client, package_in_db, token_in_db):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages?page={max_int+7}&size=20",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_le"


@pytest.mark.asyncio
async def test_package_pagination_422_size_ge(http_client, package_in_db, token_in_db):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages?page=1&size=-7",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_ge"


@pytest.mark.asyncio
async def test_package_pagination_422_page_le(http_client, package_in_db, token_in_db):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages?page=1&size={max_int+7}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "value_error.number.not_le"


@pytest.mark.asyncio
async def test_package_pagination_404(http_client, package_in_db, token_in_db):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages?page=7777&size=7777",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "This page has no items to display"}


@pytest.mark.asyncio
async def test_package_pagination_404(http_client, package_in_db, token_in_db):
    response = await http_client.get(
        f"/v1/applications/{package_in_db.application_id}/packages?page={max_int}&size={max_int}",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Offset is too big"}


@pytest.mark.asyncio
async def test_upload_package_200(
    http_client, token_in_db, upload_temp_file, package_in_db
):
    test_file_path, package_update = upload_temp_file

    async with aiofiles.open(test_file_path, "rb") as f:
        file_content = await f.read()

    response = await http_client.post(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        files={"file": ("test_file.txt", file_content)},
    )
    data = response.json()
    assert data["file"] == package_update.file
    assert data["size"] == package_update.size
    assert data["hash"] == package_update.hash
    assert data["url"] == package_update.url
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_upload_package_404_app_id(
    http_client, token_in_db, upload_temp_file_2, package_in_db
):
    test_file_path, package_update = upload_temp_file_2

    async with aiofiles.open(test_file_path, "rb") as f:
        file_content = await f.read()

    response = await http_client.post(
        f"/v1/applications/{package_in_db.application_id+3}/packages/{package_in_db.id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        files={"file": ("test_file.txt", file_content)},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_upload_package_404_pack_id(
    http_client, token_in_db, upload_temp_file_2, package_in_db
):
    test_file_path, package_update = upload_temp_file_2

    async with aiofiles.open(test_file_path, "rb") as f:
        file_content = await f.read()

    response = await http_client.post(
        f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id+3}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        files={"file": ("test_file.txt", file_content)},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "The package with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_download_package_200(http_client, token_in_db, upload_download_in_db):
    test_file_path, package_update = upload_download_in_db

    async with aiofiles.open(test_file_path, "rb") as f:
        file_content = await f.read()

    response_upload = await http_client.post(
        f"/v1/applications/{upload_download_in_db[1].application_id}/packages/{upload_download_in_db[1].id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        files={"file": ("test_file.txt", file_content)},
    )
    response_download = await http_client.get(
        f"/v1/applications/{upload_download_in_db[1].application_id}/packages/{upload_download_in_db[1].id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response_upload.json()
    assert data["file"] == package_update.file
    assert data["size"] == package_update.size
    assert data["hash"] == package_update.hash
    assert data["url"] == package_update.url
    assert response_upload.status_code == 200

    assert response_download.status_code == 200


@pytest.mark.asyncio
async def test_download_package_404_app_id(
    http_client, token_in_db, upload_download_in_db
):
    test_file_path, package_update = upload_download_in_db

    async with aiofiles.open(test_file_path, "rb") as f:
        file_content = await f.read()

    response_upload = await http_client.post(
        f"/v1/applications/{upload_download_in_db[1].application_id}/packages/{upload_download_in_db[1].id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        files={"file": ("test_file.txt", file_content)},
    )
    invalid_id = -7
    response_download = await http_client.get(
        f"/v1/applications/{invalid_id}/packages/{upload_download_in_db[1].id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response_upload.json()
    assert data["file"] == package_update.file
    assert data["size"] == package_update.size
    assert data["hash"] == package_update.hash
    assert data["url"] == package_update.url
    assert response_upload.status_code == 200

    assert response_download.status_code == 404
    assert response_download.json() == {
        "detail": "The application with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_download_package_404_pack_id(
    http_client, token_in_db, upload_download_in_db
):
    test_file_path, package_update = upload_download_in_db

    async with aiofiles.open(test_file_path, "rb") as f:
        file_content = await f.read()

    response_upload = await http_client.post(
        f"/v1/applications/{upload_download_in_db[1].application_id}/packages/{upload_download_in_db[1].id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
        files={"file": ("test_file.txt", file_content)},
    )
    invalid_id = -7
    response_download = await http_client.get(
        f"/v1/applications/{upload_download_in_db[1].application_id}/packages/{invalid_id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    data = response_upload.json()
    assert data["file"] == package_update.file
    assert data["size"] == package_update.size
    assert data["hash"] == package_update.hash
    assert data["url"] == package_update.url
    assert response_upload.status_code == 200

    assert response_download.status_code == 404
    assert response_download.json() == {
        "detail": "The package with the id requested does not exist"
    }


@pytest.mark.asyncio
async def test_download_package_404_no_file(
    http_client, token_in_db, upload_download_in_db_2
):
    response_download = await http_client.get(
        f"/v1/applications/{upload_download_in_db_2[1].application_id}/packages/{upload_download_in_db_2[1].id}/file",
        headers={"Authorization": f"Bearer {token_in_db.token}"},
    )
    assert response_download.status_code == 404
    assert response_download.json() == {"detail": "File not found"}
