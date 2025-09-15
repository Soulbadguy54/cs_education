from typing import Optional, Literal
from aiogram.fsm.storage.base import KeyBuilder, StorageKey


class CustomKeyBuilder(KeyBuilder):
    def __init__(
        self,
        *,
        prefix: str = "fsm",
        separator: str = ":",
        with_bot_id: bool = True,
    ) -> None:
        """
        :param prefix: prefix for all records
        :param separator: separator
        :param with_bot_id: include Bot id in the key
        """
        self.prefix = prefix
        self.separator = separator
        self.with_bot_id = with_bot_id

    def build(
        self,
        key: StorageKey,
        part: Optional[Literal["data", "state", "lock"]] = None,
    ) -> str:
        parts = [self.prefix]

        if self.with_bot_id:
            parts.append(str(key.bot_id))

        if key.thread_id:
            parts.append(str(key.thread_id))

        parts.append(str(key.user_id))

        if part:
            parts.append(part)
        return self.separator.join(parts)
