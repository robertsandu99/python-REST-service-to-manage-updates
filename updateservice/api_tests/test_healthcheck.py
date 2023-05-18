from http.client import HTTPException
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from updateservice.settings import setting


@pytest.mark.asyncio
async def test_healthcheck_200(http_client):
    response = await http_client.get(f"/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_healthcheck_500(http_client):
    test_engine = create_async_engine(
        "postgresql+asyncpg://user:pass@0.0.0.0:5434/wrong_pgdb"
    )
    test_async_session = sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    with patch(
        "updateservice.repositories.db_repo.async_session", new=test_async_session
    ):
        result = await http_client.get("/health")
        assert result.status_code == 500
