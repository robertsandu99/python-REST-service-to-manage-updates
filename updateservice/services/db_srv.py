from fastapi import Depends

from ..repositories.db_repo import DbConn


class PostApiServer(DbConn):
    def __init__(self, repo: DbConn = Depends(DbConn)):
        self.repo = repo

    async def check_connection(self):
        try:
            await self.repo.get_db_conn()
            return True
        except:
            return False
