from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from education_bot.misc.callbackdata import EmojiCB, ActionCB
from education_bot.misc.data import CURRENT_SUPPORT_URL


SUPPORT_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⛑️ Тех. поддержка", url=CURRENT_SUPPORT_URL)]
    ]
)


def get_emoji_challenge_kb(pairs: list[tuple[str, str]]):
    kb = InlineKeyboardBuilder()
    kb.add(
        *(
            InlineKeyboardButton(
                text=pair[1], callback_data=EmojiCB(index=index).pack()
            )
            for index, pair in enumerate(pairs)
        )
    )

    kb.adjust(5)
    kb.row(
        InlineKeyboardButton(
            text="🔁 Обновить задание",
            callback_data=ActionCB(act="refresh_emoji", data="x").pack(),
        ),
        width=1,
    )
    return kb.as_markup()
