from typing import Any
from aiogram.filters.callback_data import CallbackData


class EmojiCB(CallbackData, prefix="emoji"):
    index: int


class ActionCB(CallbackData, prefix="act"):
    act: str
    data: Any
