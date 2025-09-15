from typing import Any
from aiogram.filters.callback_data import CallbackData


class ActionCB(CallbackData, prefix="act"):
    act: str
    data: Any
