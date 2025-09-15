import asyncio
from collections import defaultdict
from functools import wraps
from typing import Callable
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


def album_handler(timeout: float = 0.5):
    # Хранилище альбомов и таймеров на уровне декоратора
    albums = defaultdict(list)
    timers = {}

    def decorator(handler: Callable):
        @wraps(handler)
        async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
            async def process_album():
                await asyncio.sleep(timeout)
                album = albums.pop(key, [])
                if album:
                    await handler(message, state, album=album)
                timers.pop(key, None)

            key = message.media_group_id or message.message_id
            albums[key].append(message)

            if key in timers:
                timers[key].cancel()

            timers[key] = asyncio.create_task(process_album())

        return wrapper

    return decorator
