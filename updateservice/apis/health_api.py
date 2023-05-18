import asyncio

from fastapi import APIRouter, Depends, HTTPException

from ..services.db_srv import PostApiServer

router = APIRouter()


@router.get("/health")
async def healthcheck(healthcheck: PostApiServer = Depends(PostApiServer)):
    response = await healthcheck.check_connection()
    if response == False:
        raise HTTPException(status_code=500, detail="No connection to db")
    else:
        return "Application is healthy"
