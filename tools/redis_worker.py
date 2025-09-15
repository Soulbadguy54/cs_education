from typing import Any
import msgpack
from arq import Worker
from arq.connections import RedisSettings, ArqRedis, create_pool
from config import CONFIG
from tools.worker_funcs import create_grenade_post


REDIS_CONFIG = CONFIG.redis_db


def job_msgpack_serialize(obj: dict[str, Any]) -> bytes:
    if "r" in obj and isinstance(obj["r"], Exception):
        obj["r"] = repr(obj["r"])
    return msgpack.packb(obj)


def create_worker(pool: ArqRedis) -> Worker:
    return Worker(
        functions=(  # type: ignore
            create_grenade_post,
        ),
        queue_name="admin_bot",
        handle_signals=False,
        keep_result=30,
        poll_delay=3,
        max_jobs=1,
        job_serializer=job_msgpack_serialize,
        job_deserializer=lambda x: msgpack.unpackb(x, raw=False),
        redis_pool=pool,
        expires_extra_ms=60000,
    )


async def create_redis_pool():
    return await create_pool(
        RedisSettings(
            host="127.0.0.1",
            port=REDIS_CONFIG.port,
            database=REDIS_CONFIG.queue_db_index,
        ),
        default_queue_name="admin_bot",
        job_serializer=job_msgpack_serialize,
        job_deserializer=lambda b: msgpack.unpackb(b, raw=False),
    )
