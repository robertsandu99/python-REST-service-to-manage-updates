import functools

from pydantic import BaseSettings, Field


class AppSettings(BaseSettings):
    host = Field("127.0.0.1")
    port = Field("8080")
    db_conn: str = Field(..., env="UPDATE_SRV_DB_CONNECTION_STRING")
    secret_key: str = "SECRET_KEY"
    endpoint: str = "ENDPOINT"
    my_access_key: str = "MY_ACCES_KEY"
    my_secret_key: str = "MY_SECRET_KEY"
    bucket_name: str = "BUCKET_NAME"
    broker_url: str = "BROKER_URL"
    POSTGRES_MAX_INT: int = 2**31 - 1
    POSTGRES_MAX_STR: str = "s" * 256

    class Config:
        env_prefix = "update_service_"
        env_file = ".env"


@functools.lru_cache
def get_settings() -> dict:
    return AppSettings().dict()


setting = get_settings()
