import asyncio
import logging.config
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
from config import CONFIG, LOGGING_CONFIG
from database.db_engine import create_db_engine, AsyncSessionMaker
from tools.deps import Dependencies
from education_bot.bot import (
    education_bot_simple_handler,
    education_bot_dispatcher,
    education_bot,
    set_education_webhook,
)
from admin_bot.bot import (
    admin_bot_simple_handler,
    admin_bot_dispatcher,
    admin_bot,
    set_admin_webhook,
)
from admin_bot.pyrogram_bot import pyro_bot
from tools.redis_worker import create_redis_pool, create_worker


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("lifespan")


# Функция завершения
async def on_shutdown(application=None):
    await education_bot.session.close()
    await admin_bot.session.close()
    await admin_bot_dispatcher.storage.close()
    await Dependencies.worker.close()
    logger.info("Service [CLOSED]")


async def main():
    app = web.Application()
    app.on_shutdown.append(on_shutdown)

    await set_education_webhook()
    await set_admin_webhook()

    education_bot_simple_handler.register(
        app, path=CONFIG.education_bot.webhook_path
    )
    admin_bot_simple_handler.register(app, path=CONFIG.admin_bot.webhook_path)

    setup_application(app, education_bot_dispatcher, bot=education_bot)
    setup_application(app, admin_bot_dispatcher, bot=admin_bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8003)
    await site.start()
    logger.info("Server on http://127.0.0.1:8003 [STARTED]")

    # Воркер
    logger.info("Starting worker...")
    admin_worker = create_worker(pool=await create_redis_pool())
    Dependencies.worker = admin_worker
    loop = asyncio.get_running_loop()
    loop.create_task(admin_worker.async_run())
    logger.info("Worker [STARTED]")

    # Подключение к БД
    logger.info("Connecting to DB...")
    AsyncSessionMaker.configure(
        bind=create_db_engine(CONFIG.db)
    )  # Подключаем sessionmaker к созданному движку
    Dependencies.db_pool = AsyncSessionMaker
    logger.info("Db connected [DONE]")

    # Пирограм
    pyro_bot.loop = loop
    pyro_bot.storage.loop = loop
    pyro_bot.dispatcher.loop = loop
    Dependencies.pyro_bot = pyro_bot

    # Боты
    Dependencies.admin_bot = admin_bot
    Dependencies.education_bot = education_bot

    async with Dependencies.pyro_bot:
        await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application [STOP]")
