from updateservice.connection_db import async_session


class DbConn:
    """Connection to db for health checking"""

    async def get_db_conn(self):
        async with async_session() as session:
            cursor = await session.execute("SELECT 1")
            result = cursor.fetchall()
            return result
