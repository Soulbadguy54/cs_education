from dataclasses import dataclass
from typing import Type
from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class RedisDB:
    port: int
    queue_db_index: int
    bot_db_index: int


@dataclass
class ServerConfig:
    url: str
    host: str
    port: int


@dataclass
class TgBot:
    bot_token: str
    webhook_path: str
    secret_string: str


@dataclass
class Config:
    server: ServerConfig
    db: DbConfig
    redis_db: RedisDB
    admin_bot: TgBot
    education_bot: TgBot
    yandex_token: str

    cs_education_channel_id: int
    cs_education_feedback_channel_id: int
    cs_education_chat_id: int
    cs_education_support_id: int
    admin_ids: list[Type[int]]
    service_id: int


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        server=ServerConfig(
            url=env.str("URL"),
            host=env.str("HOST"),
            port=env.int("PORT"),
        ),
        redis_db=RedisDB(
            port=env.int("REDIS_PORT"),
            bot_db_index=env.int("REDIS_BOT_INDEX"),
            queue_db_index=env.int("REDIS_QUEUE_INDEX"),
        ),
        db=DbConfig(
            host=env.str("HOST"),
            password=env.str("DB_PASS"),
            user=env.str("DB_USER"),
            database=env.str("DB_NAME"),
        ),
        admin_bot=TgBot(
            bot_token=env.str("ADMIN_BOT_TOKEN"),
            webhook_path=env.str("ADMIN_BOT_PATH"),
            secret_string=env.str("ADMIN_SECRET_STR"),
        ),
        education_bot=TgBot(
            bot_token=env.str("EDUCATION_BOT_TOKEN"),
            webhook_path=env.str("EDUCATION_BOT_PATH"),
            secret_string=env.str("EDUCATION_SECRET_STR"),
        ),
        cs_education_channel_id=env.int(
            "CS_EDUCATION_CHANNEL_ID"
        ),  # test -1001446982437
        cs_education_feedback_channel_id=env.int("CS_EDUCATION_FEEDBACK_CHANNEL_ID"),
        cs_education_chat_id=env.int("CS_EDUCATION_CHAT_ID"),
        cs_education_support_id=env.int("CS_EDUCATUIN_SUPPORT_ID"),
        admin_ids=env.list("ADMIN_IDS", subcast=int, delimiter=","),
        service_id=env.int("SERVICE_ID"),
        yandex_token=env.str("YANDEX_TOKEN"),
    )


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "aiogram.event": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "admin_bot": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "lifespan": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "aiohttp.access": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "education_bot": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "arq.worker": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "arq.jobs": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

CONFIG: Config = load_config(".env")
