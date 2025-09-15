from typing import Annotated
from arq import ArqRedis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.engine import AsyncSessionMaker


class Dependencies:
    queue: ArqRedis | None = None


async def get_async_session() -> AsyncSession:
    async with AsyncSessionMaker() as session:
        yield session


# Зависимость для получения Redis-пула
async def get_redis_pool() -> ArqRedis:
    return Dependencies.queue


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
QueueDep = Annotated[ArqRedis, Depends(get_redis_pool)]


# def print_logger_configs():
#     # Получаем менеджер логгеров
#     manager = logging.Logger.manager
#
#     # Получаем словарь всех зарегистрированных логгеров
#     loggers = manager.loggerDict
#
#     print("Конфигурация всех логгеров в программе:")
#     for name, logger in loggers.items():
#         # Пропускаем PlaceHolder, так как у них нет конфигурации
#         if isinstance(logger, logging.PlaceHolder):
#             continue
#
#         # Собираем информацию о логгере
#         level = logging.getLevelName(logger.level) if logger.level != 0 else "NOTSET"
#         handlers = [str(h) for h in logger.handlers] if logger.handlers else "No handlers"
#         filters = [str(f) for f in logger.filters] if logger.filters else "No filters"
#         propagate = logger.propagate
#
#         # Форматируем вывод
#         config_info = (
#             f"Logger: {name}\n"
#             f"  Level: {level}\n"
#             f"  Handlers: {handlers}\n"
#             f"  Filters: {filters}\n"
#             f"  Propagate: {propagate}\n"
#         )
#         print(config_info)
