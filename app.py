import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from starlette.middleware.cors import CORSMiddleware
from config import CONFIG, LOGGING_CONFIG
from fastapi import FastAPI, APIRouter
from db.engine import AsyncSessionMaker, create_async_engine_wrapper, create_db_tables
from dependencies import Dependencies
from redis_queue import create_redis_pool
from routers.admin_api import admin_router
from routers.grenade_api import grenade_router
from routers.user_api import user_router


logger = logging.getLogger("lifespan")


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("APP starting...")

    # Подключение к БД
    logger.info("Connecting to DB...")
    engine = create_async_engine_wrapper(CONFIG.db)
    await create_db_tables(engine)
    AsyncSessionMaker.configure(
        bind=engine
    )  # Подключаем sessionmaker к созданному движку
    logger.info("Db connected [DONE]")

    # Подключение кэша
    logger.info("Running im memory cache...")
    FastAPICache.init(InMemoryBackend())
    logger.info("In memory cache [DONE]")

    # подключение к redis
    logger.info("Connecting to Redis...")
    Dependencies.queue = await create_redis_pool()
    logger.info("Redis pool initialized [DONE]")

    # print_logger_configs()
    yield

    await FastAPICache.clear()
    logger.info("APP [STOPED]")


app = FastAPI(
    lifespan=lifespan,
    openapi_url=None,  # "/api/openapi.json",
    docs_url=None,  # "/api/docs",
    redoc_url=None,  # "/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CONFIG.server.url],  # ["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

api_router = APIRouter(tags=["API"])
api_router.include_router(user_router, prefix="/user")
api_router.include_router(grenade_router, prefix="/grenade")
api_router.include_router(admin_router, prefix="/admin")

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",  # "0.0.0.0"
        port=CONFIG.server.port,
        log_config=LOGGING_CONFIG,
    )
