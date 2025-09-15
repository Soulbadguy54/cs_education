import logging
import time
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import ChatJoinRequest, Message
from config import CONFIG
from education_bot.misc.funcs import get_random_emojis
from education_bot.misc.keyboards import get_emoji_challenge_kb, SUPPORT_KEYBOARD
from education_bot.misc.states import EmojiCaptcha
from education_bot.misc.text_templates import (
    get_emoji_challenge_text,
    get_join_request_reject_text,
)


CS_EDUCATION_CHAT_ID = CONFIG.cs_education_chat_id

logger = logging.getLogger("lifespan")

chat_router = Router(name="chat")
chat_router.chat_join_request(F.chat.id == CS_EDUCATION_CHAT_ID)
chat_router.message(F.chat.id == CS_EDUCATION_CHAT_ID)


ONE_DAY = 60 * 60 * 24  # seconds


@chat_router.chat_join_request(any_state)
async def chat_join_request_s1(request: ChatJoinRequest, state: FSMContext):
    start_tries = 1
    data = await state.get_data()
    now = round(time.time())  # seconds

    # Если юзер попробовал уже 3 раза, и время кулдауна не вышло
    if data.get("tries", start_tries) > 3:
        delta = (data["last_try_date"] + ONE_DAY) - now
        if delta > 0:
            await request.bot.send_message(
                chat_id=request.from_user.id,
                text=get_join_request_reject_text(delta),
                reply_markup=SUPPORT_KEYBOARD,
            )
            return await request.decline()

    # Если юзер первый раз или кулдаун закончился
    random_pairs, selected_index = get_random_emojis()

    await state.set_state(EmojiCaptcha.waiting_for_choice)
    await state.update_data(
        selected_index=selected_index, tries=start_tries, last_try_date=now
    )

    await request.bot.send_message(
        chat_id=request.from_user.id,
        text=get_emoji_challenge_text(
            selected_emoji_name=random_pairs[selected_index][0].capitalize(),
            language_code=request.from_user.language_code,
            tries=start_tries,
        ),
        reply_markup=get_emoji_challenge_kb(random_pairs),
    )


@chat_router.message(
    F.sender_chat.id == CONFIG.cs_education_channel_id,
    F.is_automatic_forward,
    F.from_user.id == CONFIG.service_id,
)
async def send_rule_message(message: Message):
    await message.reply(
        text="🇷🇺 <b>Правила:</b>"
        f"\n ✓ Конструктивная критика"
        "\n ✓ Вайбовое общение"
        "\n ✗ Токсичность"
        "\n ✗ Реклама"
        "\n ✗ Шлюхоботы"
        "\n ✗ Политика и ко"
        f"\n\n🇬🇧 <b>Rules:</b>"
        f"\n ✓ Constructive criticism"
        "\n ✓ Vibe talks"
        "\n ✗ Toxicity"
        "\n ✗ Advertising"
        "\n ✗ Bots"
        "\n ✗ Politics",
    )
