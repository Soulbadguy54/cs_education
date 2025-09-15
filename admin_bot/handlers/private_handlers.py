import logging
from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.types import Message, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from admin_bot.misc.callbackdata import ActionCB
from admin_bot.misc.keyboards import RELOAD_KEYBOARD
from admin_bot.misc.objects import UploadData
from config import CONFIG
from admin_bot.misc.states import UploadGrenade, AdminStates
from database.models import Grenade, GrenadeTelegramData
from tools.deps import Dependencies


private_router = Router(name="admin")
private_router.message.filter(
    F.chat.type == ChatType.PRIVATE,
    F.from_user.id.in_(CONFIG.admin_ids)
)
private_router.callback_query.filter(
    F.message.chat.type == ChatType.PRIVATE,
    F.from_user.id.in_(CONFIG.admin_ids)
)

logger = logging.getLogger("lifespan")


async def insert_data_in_db(state_data: UploadData) -> int:
    async with Dependencies.db_pool() as session:
        stm = (
            insert(Grenade)
            .values(
                tg_data=GrenadeTelegramData(
                    video_file_id=state_data["video"],
                    video_duration=state_data["video_duration"],
                    setup_photo_file_id=state_data["setup_photo"],
                    finish_photo_file_id=state_data["finish_photo"],
                    cover_file_id=state_data["cover_photo"],
                ).model_dump()
            )
            .returning(Grenade.id)
        )

        grenade_id: int = (await session.execute(stm)).scalar()
        await session.commit()
        logger.info(f"Предварительные данные гранаты [ID: {grenade_id}] успешно добавлены в БД")
    return grenade_id


@private_router.message(any_state, Command(commands="new_grenade"))
@private_router.message(any_state, CommandStart())
async def add_grenade_s1(message: Message, state: FSMContext):
    await message.answer("1️⃣ Пришли видео в формате mp4")
    await state.set_state(UploadGrenade.waiting_for_video)


@private_router.message(UploadGrenade.waiting_for_video)
async def add_grenade_s2(message: Message, state: FSMContext):
    video_file = message.video

    if not video_file:
        return await message.answer("❗ Это не видео")

    await message.answer("\n\n✅ Видео успешно загружено\n\n2️⃣ Пришли изображение с <b>СЕТАПОМ</b>")
    await state.set_state(UploadGrenade.waiting_for_setup_pic)
    await state.update_data(
        UploadData(video=video_file.file_id, video_duration=video_file.duration)
    )


@private_router.message(UploadGrenade.waiting_for_setup_pic)
async def add_grenade_s3(message: Message, state: FSMContext):
    photo_files = message.photo

    if not photo_files:
        return await message.answer("❗ Это не фото")

    await message.answer(
        "\n\n✅ Фото сетапа успешно загружено"
        "\n\n3️⃣ Пришли изображение с <b>ФИНАЛЬНОЙ ТОЧКОЙ</b>"
    )
    await state.set_state(UploadGrenade.waiting_for_finish_pic)
    await state.update_data(UploadData(setup_photo=photo_files[0].file_id))


@private_router.message(UploadGrenade.waiting_for_finish_pic)
async def add_grenade_s4(message: Message, state: FSMContext):
    photo_files = message.photo

    if not photo_files:
        return await message.answer("❗ Это не фото")

    target_photo_id = photo_files[0].file_id
    await state.update_data(
        UploadData(finish_photo=target_photo_id, cover_photo=target_photo_id)
    )

    async with ChatActionSender.upload_photo(bot=message.bot, chat_id=message.chat.id):
        state_data: UploadData = await state.get_data()
        grenade_id = await insert_data_in_db(state_data)

        if not grenade_id:
            await state.set_state(UploadGrenade.checking_data)
            return await message.answer(
                "☠️ Ошибка загрузки в базу данных. Попробуй ещё раз",
                reply_markup=RELOAD_KEYBOARD,
            )

        server_url = "https://cs-education.ru"
        url = f"{server_url}/admin?method=create&id={grenade_id}"

    await message.answer(
        "✅ <i>Все данные загружены в БД</i>"
        f'\n\n🔗 Вот ссылка для перехода в админку: <a href="{url}">тык</a>'
    )
    await state.clear()


@private_router.callback_query(UploadGrenade.checking_data, ActionCB.filter(F.act == "upload_files"))
async def add_grenade_s4_retry(query: CallbackQuery, callback_data: ActionCB, state: FSMContext):
    async with ChatActionSender.upload_photo(bot=query.bot, chat_id=query.message.chat.id):
        state_data: UploadData = await state.get_data()
        grenade_id = await insert_data_in_db(state_data)

        if not grenade_id:
            return await query.answer("☠️ Всё ещё ошибка, попробуй позже")

        server_url = "https://cs-education.ru"
        url = f"{server_url}/admin?method=create&id={grenade_id}"

    await query.message.edit_text(
        "✅ <i>Все данные загружены в БД</i>"
        f'\n\n🔗 Вот ссылка для перехода в админку: <a href="{url}">тык</a>'
    )
    await state.clear()


# ---------------------------------------------------- УДАЛЕНИЕ ВИДЕО --------------------------------------------------
@private_router.message(
    any_state,
    F.forward_from_chat & F.media_group_id & F.forward_origin.chat.id == CONFIG.cs_education_channel_id,
)
async def delete_video(message: Message):
    async with Dependencies.db_pool() as session:
        stm = (
            delete(Grenade)
            .where(Grenade.tg_post_id == message.forward_origin.message_id)
            .returning(Grenade.tg_post_id, Grenade.tg_data)
        )
        tg_post_id, tg_data = (await session.execute(stm)).fetchone()

        if not tg_post_id:
            return await message.reply("❗ Это не пост с гранатой")

        if await message.bot.delete_messages(
            chat_id=CONFIG.cs_education_channel_id,
            message_ids=[
                tg_post_id,
                tg_data.setup_photo_msg_id,
                tg_data.finish_photo_msg_id,
            ],
        ):
            await session.commit()
            await message.reply("✅ Граната и пост удалены")
        else:
            await session.rollback()
            await message.reply("❗ Ошибка при удалении гранаты")


# ------------------------------------------------------ ЧЕК ФАЙЛА -----------------------------------------------------
@private_router.message(Command(commands="file"))
async def file_check(message: Message, state: FSMContext):
    await message.answer("Жду файл")
    await state.set_state(AdminStates.waiting_for_file)


@private_router.message(AdminStates.waiting_for_file)
async def answer_file_type(message: Message):
    if message.video:
        text = message.video.file_id + "\n\n" + message.content_type
    elif message.document:
        text = message.document.file_id + "\n\n" + message.content_type
    elif message.photo:
        text = message.photo[-1].file_id + "\n\n" + message.content_type
    elif message.animation:
        text = message.animation.file_id + "\n\n" + message.content_type
    else:
        text = "Это не файл"

    await message.answer(text)


# ------------------------------------------------ УДАЛЕНИЕ ДРУГИХ СООБЩЕНИЙ ------------------------------------------
@private_router.message()
async def delete_message(message: Message):
    await message.delete()
