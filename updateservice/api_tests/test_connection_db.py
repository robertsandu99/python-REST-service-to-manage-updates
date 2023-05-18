import pytest

from updateservice.connection_db import async_session


@pytest.mark.asyncio
async def test_connection_db():
    async with async_session() as session:
        cursor = await session.execute("select 100 as dummy")
        result = cursor.fetchall()
    assert len(result) == 1
    assert result[0].dummy == 100
