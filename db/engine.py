from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.sql.ddl import CreateSchema
from sqlmodel import SQLModel
from config import DbConfig


def create_async_engine_wrapper(config: DbConfig) -> AsyncEngine:
    return create_async_engine(
        f"postgresql+asyncpg://{config.user}:{config.password}@{config.host}/{config.database}"
    )


async def create_db_tables(async_engine):
    async with async_engine.begin() as conn:
        await conn.execute(CreateSchema("public", if_not_exists=True))
        await conn.run_sync(SQLModel.metadata.create_all, checkfirst=True)


# Инициализация асинхронного sessionmaker
AsyncSessionMaker = async_sessionmaker(
    bind=None,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)
