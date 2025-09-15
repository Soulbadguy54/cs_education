from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
)
from config import DbConfig


def create_db_engine(config: DbConfig) -> AsyncEngine:
    return create_async_engine(
        url=make_url(f"postgresql+asyncpg://{config.user}:{config.password}@{config.host}/{config.database}"),
        pool_pre_ping=True,
    )


# Инициализация асинхронного sessionmaker
AsyncSessionMaker = async_sessionmaker(
    bind=None,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)
