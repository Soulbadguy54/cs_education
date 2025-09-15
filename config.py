from dataclasses import dataclass
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


@dataclass
class ServerConfig:
    url: str
    host: str
    port: int


@dataclass
class AdminData:
    username: str
    password_hash: str
    secret_key: str


@dataclass
class Config:
    server: ServerConfig
    db: DbConfig
    redis_db: RedisDB
    admin_data: AdminData
    bot_token: str


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        server=ServerConfig(
            url=env.str("URL"),
            host=env.str("HOST"),
            port=env.int("PORT"),
        ),
        db=DbConfig(
            host=env.str("HOST"),
            password=env.str("DB_PASS"),
            user=env.str("DB_USER"),
            database=env.str("DB_NAME"),
        ),
        redis_db=RedisDB(
            port=env.int("REDIS_PORT"),
            queue_db_index=env.int("REDIS_QUEUE_INDEX"),
        ),
        admin_data=AdminData(
            username=env.str("ADMIN_USERNAME"),
            password_hash=env.str("ADMIN_PASSWORD_HASH"),
            secret_key=env.str("SECRET_KEY"),
        ),
        bot_token=env.str("BOT_TOKEN"),
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
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "fastapi": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "api_logger": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "arq.jobs": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        # "sqlalchemy": {
        #     "level": "INFO",
        #     "handlers": ["console"],
        #     "propagate": False,
        # },
        "lifespan": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

CONFIG: Config = load_config(".env")
