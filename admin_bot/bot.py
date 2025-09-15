import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from admin_bot.middlewares.trottling_middleware import OuterThrottlingMiddleware
from config import CONFIG
from admin_bot.handlers.private_handlers import private_router
from admin_bot.handlers.channel_handler import channel_router
from tools.deps import REDIS_CONNECTION
from tools.key_builders import CustomKeyBuilder


logger = logging.getLogger("admin_bot")


admin_bot_dispatcher = Dispatcher(
    storage=RedisStorage(
        redis=REDIS_CONNECTION,
        data_ttl=604800,  # неделя
        state_ttl=604800,
        key_builder=CustomKeyBuilder(),
    )
)
admin_bot_dispatcher.message.outer_middleware(OuterThrottlingMiddleware())
admin_bot_dispatcher.callback_query.outer_middleware(OuterThrottlingMiddleware())
admin_bot_dispatcher.include_routers(
    channel_router,
    private_router,
)

admin_bot = Bot(
    token=CONFIG.admin_bot.bot_token,
    default=DefaultBotProperties(
        parse_mode="HTML",
        link_preview_is_disabled=True,
    ),
)

admin_bot_simple_handler = SimpleRequestHandler(
    dispatcher=admin_bot_dispatcher, bot=admin_bot
)


async def set_admin_webhook():
    # На конце не должно быть слэша - это важно для fastapi
    webhook_url = (CONFIG.server.url + CONFIG.admin_bot.webhook_path)
    allowed_updates = [
        "message",
        "callback_query",
        "message_reaction_count",
        "chat_member",
    ]

    webhook_data = await admin_bot.get_webhook_info()
    if webhook_data.url != webhook_url or webhook_data.allowed_updates != allowed_updates:
        logger.info(f"Set admin TG webhook on {webhook_url}")
        await admin_bot.set_webhook(
            url=webhook_url,
            secret_token=CONFIG.admin_bot.secret_string,
            allowed_updates=allowed_updates,
        )
        webhook_data = await admin_bot.get_webhook_info()
    logger.info(webhook_data)

    await admin_bot.set_my_commands(
        commands=[
            BotCommand(command="new_grenade", description="Добавить гранату 💣"),
        ],
        scope=BotCommandScopeAllPrivateChats(),
    )

    return webhook_data
