import logging
import time
from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from config import CONFIG
from database.models import Grenade, UserFavourite, User
from education_bot.misc.callbackdata import ActionCB, EmojiCB
from education_bot.misc.funcs import get_random_emojis
from education_bot.misc.keyboards import get_emoji_challenge_kb, SUPPORT_KEYBOARD
from education_bot.misc.states import Feedback, EmojiCaptcha
from education_bot.misc.text_templates import (
    get_emoji_challenge_text,
    get_join_request_reject_text,
)
from tools.deps import Dependencies


private_router = Router(name="private")
private_router.message_reaction_count.filter(F.chat.type == ChatType.PRIVATE)
private_router.message.filter(F.chat.type == ChatType.PRIVATE)
private_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)

logger = logging.getLogger("lifespan")


# ------------------------------------------------------ FEEDBACK -----------------------------------------------------
@private_router.message(
    any_state, CommandStart(deep_link=True, magic=F.args == "feedback")
)
async def conversation_for_feedback_s1(message: Message, state: FSMContext):
    if message.from_user.language_code == "ru":
        text = (
            "❤️ Хочешь сказать какие мы крутые?"
            "\n☠️ Нашёл жесточенный баг?"
            "\n🤡 Чисто рядовой хейтер?"
            "\n\n✍️ Пиши свой отзыв! Мы обязательно прочитаем и, возможно, посмеёмся"
        )
    else:
        text = (
            "❤️ Do you want to tell us how cool we are?"
            "\n☠️ Found a nasty bug?"
            "\n🤡 Just a regular hater?"
            "\n\n✍️ Write your review! We will read it for sure and maybe even laugh"
        )

    await message.answer(text)
    await state.set_state(Feedback.waiting_for_text)


@private_router.message(Feedback.waiting_for_text)
async def conversation_for_feedback_s2(message: Message, state: FSMContext):
    if message.from_user.language_code == "ru":
        text = "🤜🤛 Спасибо за фидбэк!"
    else:
        text = "🤜🤛 Thanks for the feedback!"

    await message.answer(text)
    await state.clear()

    text = message.html_text + f"\n\n🗣️ {message.from_user.full_name}"

    await message.bot.send_message(
        chat_id=CONFIG.cs_education_feedback_channel_id, text=text
    )


# -------------------------------------------------- CHAT REQUEST -----------------------------------------------------
@private_router.callback_query(
    EmojiCaptcha.waiting_for_choice, ActionCB.filter(F.act == "refresh_emoji")
)
async def chat_join_request_refresh(
    query: CallbackQuery,
    callback_data: ActionCB | EmojiCB,
    state: FSMContext,
    need_query_answer=True,
):
    now = round(time.time())  # seconds

    data = await state.get_data()
    await state.update_data(tries=data["tries"] + 1, last_try_date=now)

    # Если попытки закончились
    if data["tries"] > 3:
        await query.message.edit_text(
            text=get_join_request_reject_text(query.message.from_user.language_code),
            reply_markup=SUPPORT_KEYBOARD,
        )
        if need_query_answer:
            await query.answer()
        return await query.bot.decline_chat_join_request(
            chat_id=CONFIG.cs_education_chat_id, user_id=query.from_user.id
        )

    # Если попытки ещё есть
    random_pairs, selected_index = get_random_emojis()
    await state.update_data(selected_index=selected_index)

    if need_query_answer:
        await query.answer(
            {"ru": "🔁 Обновляем"}.get(
                query.message.from_user.language_code, "🔁 Reloading"
            )
        )

    await query.message.edit_text(
        text=get_emoji_challenge_text(
            selected_emoji_name=random_pairs[selected_index][0].capitalize(),
            language_code=query.message.from_user.language_code,
            tries=data["tries"] + 1,
        ),
        reply_markup=get_emoji_challenge_kb(random_pairs),
    )


@private_router.callback_query(EmojiCaptcha.waiting_for_choice, EmojiCB.filter())
async def chat_join_request_s2(
    query: CallbackQuery, callback_data: EmojiCB, state: FSMContext
):
    redis_data = await state.get_data()
    if redis_data["selected_index"] == callback_data.index:
        await query.answer(
            {"ru": "✅ Всё верно"}.get(
                query.message.from_user.language_code, "✅ Its right"
            )
        )
        await query.message.edit_text(
            text="🥳 Поздравляю, ты в деле!",
            reply_markup=None,
        )
        await state.clear()

        await query.bot.approve_chat_join_request(
            chat_id=CONFIG.cs_education_chat_id, user_id=query.from_user.id
        )
    else:
        await query.answer("❌ Ошибочка")
        await chat_join_request_refresh(
            query, callback_data, state, need_query_answer=False
        )


# -------------------------------------------------- Изрбранное -----------------------------------------------------
@private_router.message(F.forward_from_chat & F.media_group_id)
async def add_to_favourite(message: Message):
    from_chat_id = message.forward_from_chat.id

    if from_chat_id != CONFIG.cs_education_channel_id:
        return message.reply("❌ Этот сетап не из нашего канала")

    async with (
        ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id),
        Dependencies.db_pool() as session,
    ):
        stm = select(Grenade.id).where(
            Grenade.tg_post_id == message.forward_origin.message_id
        )
        grenade_id = (await session.execute(stm)).scalar()

        if not grenade_id:
            return message.reply("❌ Не нашел такой гранаты")

        try:
            stm = (
                insert(UserFavourite)
                .values(user_id=message.from_user.id, grenade_id=grenade_id)
                .on_conflict_do_nothing()
            )
            await session.execute(stm)
            await session.commit()
        except IntegrityError:  # Юзер не зареган
            await session.rollback()
            user = message.from_user
            stm = insert(User).values(
                id=user.id,
                username=user.username,
                user_data={"name": user.full_name, "language_code": user.language_code},
            )
            await session.execute(stm)

            stm = (
                insert(UserFavourite)
                .values(user_id=message.from_user.id, grenade_id=grenade_id)
                .on_conflict_do_nothing()
            )
            await session.execute(stm)
            await session.commit()

    await message.reply(
        "✅ Добавил сетап в избранное"
        '\n\n🗑️ Удалить его можно через <a href="https://t.me/cs2education_bot/app">мини-приложение</a>'
    )
