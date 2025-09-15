import logging
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from cachetools import TTLCache


logger = logging.getLogger("lifespan")


class OuterThrottlingMiddleware(BaseMiddleware):
    cache = TTLCache(maxsize=5000, ttl=0.5)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        if (user_id := event.from_user.id) in self.cache:
            return

        self.cache[user_id] = None
        return await handler(event, data)
