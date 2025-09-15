from aiogram import Bot
from arq import Worker
from redis.asyncio import Redis
from sqlalchemy.orm import sessionmaker
from admin_bot.pyrogram_bot import PyrogramClient
from config import CONFIG


class Dependencies:
    worker: Worker | None = None
    db_pool: sessionmaker | None = None
    pyro_bot: PyrogramClient | None = None
    admin_bot: Bot | None = None
    education_bot: Bot | None = None


REDIS_CONNECTION = Redis(
    host="127.0.0.1", port=CONFIG.redis_db.port, db=CONFIG.redis_db.bot_db_index
)


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
#         handlers = (
#             [str(h) for h in logger.handlers] if logger.handlers else "No handlers"
#         )
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
