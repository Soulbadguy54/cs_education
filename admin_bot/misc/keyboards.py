from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from admin_bot.misc.callbackdata import ActionCB


RELOAD_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔄 Проверить заново",
                callback_data=ActionCB(act="upload_files", data="x").pack(),
            )
        ]
    ]
)
