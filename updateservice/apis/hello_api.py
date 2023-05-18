from fastapi import APIRouter, Depends

from ..services.hello_srv import HelloSrv

router = APIRouter(
    prefix="/temp",
    tags=["temp"],
)


@router.get("/hello")
async def say_hello(name_id: int = 0, hello_srv: HelloSrv = Depends(HelloSrv)):
    return hello_srv.say_hello(name_id)
