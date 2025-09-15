import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommandScopeDefault
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from config import CONFIG
from education_bot.handlers.chat_handlers import chat_router
from education_bot.handlers.private_handlers import private_router
from education_bot.middlewares.trottling_middleware import OuterThrottlingMiddleware
from tools.deps import REDIS_CONNECTION
from tools.key_builders import CustomKeyBuilder


logger = logging.getLogger("education_bot")


education_bot_dispatcher = Dispatcher(
    storage=RedisStorage(
        redis=REDIS_CONNECTION,
        data_ttl=604800,  # неделя
        state_ttl=604800,
        key_builder=CustomKeyBuilder(),
    )
)
education_bot_dispatcher.message.outer_middleware(OuterThrottlingMiddleware())
education_bot_dispatcher.callback_query.outer_middleware(OuterThrottlingMiddleware())
education_bot_dispatcher.include_routers(
    private_router,
    chat_router,
)

education_bot = Bot(
    token=CONFIG.education_bot.bot_token,
    default=DefaultBotProperties(
        parse_mode="HTML",
        link_preview_is_disabled=True,
    ),
)

education_bot_simple_handler = SimpleRequestHandler(
    dispatcher=education_bot_dispatcher, bot=education_bot
)


async def set_education_webhook():
    webhook_url = CONFIG.server.url + CONFIG.education_bot.webhook_path
    allowed_updates = ["message", "callback_query", "chat_join_request"]

    webhook_data = await education_bot.get_webhook_info()
    if webhook_data.url != webhook_url or webhook_data.allowed_updates != allowed_updates:
        logger.info(f"Set education_bot TG webhook on {webhook_url}")
        await education_bot.set_webhook(
            url=webhook_url,
            secret_token=CONFIG.education_bot.secret_string,
            allowed_updates=allowed_updates,
        )
        webhook_data = await education_bot.get_webhook_info()
    logger.info(webhook_data)

    await education_bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await education_bot.delete_my_commands(scope=BotCommandScopeDefault())
    return webhook_data
