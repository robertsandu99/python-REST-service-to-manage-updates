from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import (  # helps with multiple models files
    declarative_base,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from updateservice.settings import setting

engine = create_async_engine(setting["db_conn"], echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

celery_engine = create_async_engine(
    setting["db_conn"], echo=True, future=True, poolclass=NullPool
)
celery_async_session = sessionmaker(
    celery_engine, expire_on_commit=False, class_=AsyncSession
)


Base = declarative_base()


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
