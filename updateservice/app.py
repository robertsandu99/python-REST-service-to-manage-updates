from fastapi import Depends, FastAPI

from updateservice.utils.token_authentication import check_token_authentication

from .apis import (
    application_api,
    application_group_api,
    health_api,
    hello_api,
    package_api,
    team_api,
    tokens_api,
    user_api,
)


def _register_api_handlers(app: FastAPI) -> FastAPI:
    app.include_router(hello_api.router)
    app.include_router(health_api.router)
    app.include_router(team_api.router)
    app.include_router(
        application_api.router, dependencies=[Depends(check_token_authentication)]
    )
    app.include_router(user_api.router)
    app.include_router(tokens_api.router)
    app.include_router(
        package_api.router, dependencies=[Depends(check_token_authentication)]
    )
    app.include_router(
        application_group_api.router, dependencies=[Depends(check_token_authentication)]
    )
    return app


def create_app() -> FastAPI:
    """Create and return FastAPI application."""
    app = FastAPI()
    app = _register_api_handlers(app)
    return app


app = create_app()
