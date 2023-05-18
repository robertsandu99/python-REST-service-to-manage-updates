import asyncio
import hashlib
import os
import random
import shutil
import string
from datetime import datetime, timedelta

import aiofiles
import aiofiles.os
import jwt
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound

from updateservice.connection_db import async_session
from updateservice.models.application import Application
from updateservice.models.application_group import ApplicationGroup, Group
from updateservice.models.package import Package
from updateservice.models.schema import TeamCreate, TeamUpdate, UserCreate
from updateservice.models.schema_application import ApplicationCreate, ApplicationPatch
from updateservice.models.schema_application_group import GroupCreate
from updateservice.models.schema_package import PackageCreate
from updateservice.models.token import Token
from updateservice.models.user_teams import Team, User
from updateservice.settings import setting

from ..app import app


@pytest_asyncio.fixture(scope="session")
async def http_client():
    async with AsyncClient(app=app, base_url="http://0.0.0.0:8080") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_async_session():
    session = async_session()
    try:
        yield session
        await session.execute(
            "TRUNCATE teams, tokens, applications, packages, users, groups, applications_groups CASCADE"
        )
        await session.commit()
    except Exception as e:
        raise e
    finally:
        await session.close()


def random_string():
    return "".join(random.choices(string.ascii_lowercase, k=10))


def random_id():
    return random.randint(0, 999999)


def random_version_string():
    x = random.randint(0, 999)
    y = random.randint(0, 999)
    z = random.randint(0, 999)
    return f"{x}.{y}.{z}"


@pytest_asyncio.fixture
async def team_in_db(db_async_session):
    random_team_name = random_string()
    random_team_description = random_string()
    random_team_id = random_id()
    new_team = Team(
        id=random_team_id, name=random_team_name, description=random_team_description
    )
    db_async_session.add(new_team)
    await db_async_session.commit()
    yield new_team
    await db_async_session.delete(new_team)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def team_in_db_2(db_async_session):
    random_team_name = random_string()
    random_team_description = random_string()
    random_team_id = random_id()
    new_team = Team(
        id=random_team_id, name=random_team_name, description=random_team_description
    )
    db_async_session.add(new_team)
    await db_async_session.commit()
    yield new_team
    await db_async_session.delete(new_team)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def team_obj():
    random_team_name = random_string()
    random_team_description = random_string()
    yield TeamCreate(name=random_team_name, description=random_team_description)


@pytest_asyncio.fixture
async def update_team_obj():
    random_team_name = random_string()
    random_team_description = random_string()
    yield TeamUpdate(name=random_team_name, description=random_team_description)


@pytest_asyncio.fixture
async def application_in_db(db_async_session, team_in_db):
    random_app_name = random_string()
    random_app_description = random_string()
    random_app_id = random_id()
    new_app = Application(
        id=random_app_id,
        name=random_app_name,
        description=random_app_description,
        team_id=team_in_db.id,
    )
    db_async_session.add(new_app)
    await db_async_session.commit()
    yield new_app
    await db_async_session.delete(new_app)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def application_in_db_2(db_async_session, team_in_db):
    random_app_name = random_string()
    random_app_description = random_string()
    random_app_id = random_id()
    new_app = Application(
        id=random_app_id,
        name=random_app_name,
        description=random_app_description,
        team_id=team_in_db.id,
    )
    db_async_session.add(new_app)
    await db_async_session.commit()
    yield new_app
    await db_async_session.delete(new_app)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def application_obj():
    random_app_name = random_string()
    random_app_description = random_string()
    yield ApplicationCreate(name=random_app_name, description=random_app_description)


@pytest_asyncio.fixture
async def update_application_obj():
    random_app_name = random_string()
    random_app_description = random_string()
    yield ApplicationPatch(name=random_app_name, description=random_app_description)


@pytest_asyncio.fixture
async def user_in_db(db_async_session):
    random_user_email = random_string()
    random_user_name = random_string()
    random_user_id = random_id()
    new_team = User(
        id=random_user_id, email=random_user_email, full_name=random_user_name
    )
    db_async_session.add(new_team)
    await db_async_session.commit()
    yield new_team
    await db_async_session.delete(new_team)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def user_in_db_2(db_async_session):
    random_user_email = random_string()
    random_user_name = random_string()
    random_user_id = random_id()
    new_team = User(
        id=random_user_id, email=random_user_email, full_name=random_user_name
    )
    db_async_session.add(new_team)
    await db_async_session.commit()
    yield new_team
    await db_async_session.delete(new_team)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def user_obj():
    random_user_email = random_string()
    random_user_name = random_string()
    yield UserCreate(email=random_user_email, full_name=random_user_name)


jwt_secret = setting["secret_key"]


@pytest_asyncio.fixture
async def token_in_db(db_async_session, user_in_db):
    exp = datetime.now() + timedelta(seconds=120)
    payload = {"user_id": user_in_db.id, "exp": exp}
    encoded_jwt = jwt.encode(payload, jwt_secret, algorithm="HS256")
    new_token = Token(user_id=user_in_db.id, token=encoded_jwt)
    db_async_session.add(new_token)
    await db_async_session.commit()
    yield new_token
    await db_async_session.delete(new_token)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def package_in_db(db_async_session, application_in_db):
    random_version = random_version_string()
    random_description = random_string()
    random_package_id = random_id()
    new_package = Package(
        id=random_package_id,
        application_id=application_in_db.id,
        version=random_version,
        description=random_description,
        file=None,
        size=None,
        hash=None,
        url=None,
    )
    db_async_session.add(new_package)
    await db_async_session.commit()

    yield new_package

    try:
        await db_async_session.execute(
            delete(Package).filter(
                Package.id == random_package_id,
                Package.application_id == application_in_db.id,
            )
        )
        await db_async_session.commit()
    except NoResultFound:
        pass


@pytest_asyncio.fixture
async def package_in_db_2(db_async_session, application_in_db):
    random_version = random_version_string()
    random_description = random_string()
    random_package_id = random_id()
    new_package = Package(
        id=random_package_id,
        application_id=application_in_db.id,
        version=random_version,
        description=random_description,
        file=None,
        size=None,
        hash=None,
        url=None,
    )
    db_async_session.add(new_package)
    await db_async_session.commit()

    yield new_package

    try:
        await db_async_session.execute(
            delete(Package).filter(
                Package.id == random_package_id,
                Package.application_id == application_in_db.id,
            )
        )
        await db_async_session.commit()
    except NoResultFound:
        pass


@pytest_asyncio.fixture
async def package_obj():
    random_version = random_version_string()
    random_description = random_string()
    new_package = PackageCreate(version=random_version, description=random_description)
    yield new_package


async def write_random_test_file():
    get_cwd = os.getcwd()
    storage_path = f"{get_cwd}/Storage"
    test_path = os.path.join(storage_path, "test_storage")
    test_file_path = os.path.join(test_path, "test_file.txt")
    if not os.path.exists(test_path):
        os.makedirs(test_path)
    content = "my testing text file"
    encoded_content = content.encode()
    async with aiofiles.open(test_file_path, "wb") as f:
        await f.write(encoded_content)
    test_file_name = os.path.basename(test_file_path)
    file_stat = await aiofiles.os.stat(test_file_path)
    test_file_size = file_stat.st_size
    async with aiofiles.open(test_file_path, "rb") as f:
        file_bytes = await f.read()
        test_file_hash = hashlib.sha256(file_bytes).hexdigest()
    return test_file_path, test_file_name, test_file_size, test_file_hash


@pytest_asyncio.fixture
async def upload_temp_file(package_in_db):

    (
        test_file_path,
        test_file_name,
        test_file_size,
        test_file_hash,
    ) = await write_random_test_file()
    package_update = Package(
        id=package_in_db.id,
        application_id=package_in_db.application_id,
        file=test_file_name,
        size=test_file_size,
        hash=test_file_hash,
        url=f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file",
    )

    yield test_file_path, package_update
    cwd = os.getcwd()
    shutil.rmtree(f"{cwd}/Storage/Package_{package_in_db.id}")
    os.remove(test_file_path)


@pytest_asyncio.fixture
async def upload_temp_file_2(package_in_db):

    (
        test_file_path,
        test_file_name,
        test_file_size,
        test_file_hash,
    ) = await write_random_test_file()
    package_update = Package(
        id=package_in_db.id,
        application_id=package_in_db.application_id,
        file=test_file_name,
        size=test_file_size,
        hash=test_file_hash,
        url=f"/v1/applications/{package_in_db.application_id}/packages/{package_in_db.id}/file",
    )
    yield test_file_path, package_update
    os.remove(test_file_path)


@pytest_asyncio.fixture
async def upload_download_in_db(db_async_session, application_in_db):

    (
        test_file_path,
        test_file_name,
        test_file_size,
        test_file_hash,
    ) = await write_random_test_file()
    r_version = random_version_string()
    r_id = random.randint(1, 989898)
    package_update = Package(
        id=r_id,
        version=r_version,
        application_id=application_in_db.id,
        file=test_file_name,
        size=test_file_size,
        hash=test_file_hash,
        url=f"/v1/applications/{application_in_db.id}/packages/{r_id}/file",
    )
    db_async_session.add(package_update)
    await db_async_session.commit()
    yield test_file_path, package_update

    await db_async_session.delete(package_update)
    await db_async_session.commit()
    os.remove(test_file_path)
    cwd = os.getcwd()
    shutil.rmtree(f"{cwd}/Storage/Package_{package_update.id}")


@pytest_asyncio.fixture
async def upload_download_in_db_2(db_async_session, application_in_db):

    (
        test_file_path,
        test_file_name,
        test_file_size,
        test_file_hash,
    ) = await write_random_test_file()
    r_version = random_version_string()
    r_id = random.randint(1, 989898)
    package_update = Package(
        id=r_id,
        version=r_version,
        application_id=application_in_db.id,
        file=test_file_name,
        size=test_file_size,
        hash=test_file_hash,
        url=f"/v1/applications/{application_in_db.id}/packages/{r_id}/file",
    )
    db_async_session.add(package_update)
    await db_async_session.commit()
    yield test_file_path, package_update
    await db_async_session.delete(package_update)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def group_in_db(db_async_session):
    random_group_name = random_string()
    random_group_id = random_id()
    new_group = Group(id=random_group_id, name=random_group_name)
    db_async_session.add(new_group)
    await db_async_session.commit()
    yield new_group
    await db_async_session.delete(new_group)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def group_in_db_2(db_async_session):
    random_group_name = random_string()
    random_group_id = random_id()
    new_group = Group(id=random_group_id, name=random_group_name)
    db_async_session.add(new_group)
    await db_async_session.commit()
    yield new_group


@pytest_asyncio.fixture
async def group_obj():
    random_group_name = random_string()
    yield GroupCreate(name=random_group_name)


@pytest_asyncio.fixture
async def application_group_in_db(db_async_session, application_in_db, group_in_db):
    random_group_id = random_id()
    new_application_group = ApplicationGroup(
        id=random_group_id, application_id=application_in_db.id, group_id=group_in_db.id
    )
    db_async_session.add(new_application_group)
    await db_async_session.commit()
    yield new_application_group
    await db_async_session.delete(new_application_group)
    await db_async_session.commit()


@pytest_asyncio.fixture
async def application_group_in_db_2(db_async_session, application_in_db, group_in_db):
    random_group_id = random_id()
    new_application_group = ApplicationGroup(
        id=random_group_id, application_id=application_in_db.id, group_id=group_in_db.id
    )
    db_async_session.add(new_application_group)
    await db_async_session.commit()
    yield new_application_group
