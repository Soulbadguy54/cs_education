import msgpack
from arq import create_pool
from arq.connections import RedisSettings


async def create_redis_pool():
    return await create_pool(
        RedisSettings(host="127.0.0.1", port=6379, database=1),
        default_queue_name="admin_bot",
        job_serializer=msgpack.packb,
        job_deserializer=lambda b: msgpack.unpackb(b, raw=False),
    )
