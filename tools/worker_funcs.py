import asyncio
import logging
from typing import TypedDict
from aiogram import Bot
from aiogram.types import InputMediaVideo, InputMediaPhoto
from config import CONFIG
from database.models import GrenadeForWorker
from tools.deps import Dependencies
from admin_bot.misc.data import ICONS, NEW_LINE, CS_ROUND_DURATION, BOT_URL, CHANNEL_URL
from admin_bot.pyrogram_bot import PyrogramClient


logger = logging.getLogger("admin_bot")


class CreateGrenadeJobResponse(TypedDict):
    tg_post_id: int
    setup_photo_msg_id: int
    finish_photo_msg_id: int


def get_grenade_tg_post_text(grenade: GrenadeForWorker) -> str:
    additional_info = ""
    if grenade.data.additional_info:
        additional_info = (
            NEW_LINE + ICONS["special"]["info"] + " " + grenade.data.additional_info
        )

    best_timing = ""
    if grenade.data.best_timing:
        seconds_timing = CS_ROUND_DURATION - grenade.data.best_timing
        best_timing = (
            NEW_LINE
            + ICONS["special"]["timing"]
            + f" {seconds_timing // 60}:{seconds_timing % 60}"
        )

    return (
        f"<b>{ICONS['cs_maps'][grenade.map.value]} {grenade.map.value}  {ICONS['grenades'][grenade.type.value]} {grenade.type.value}</b>"
        f"\n"
        f"\n{ICONS['sides'][grenade.side.value]} {grenade.initial_position.name} ➜ {grenade.final_position.name}"
        f"\n"
        f"\n{ICONS['difficult'][grenade.difficult]} {grenade.key_combo.text}"
        f"{best_timing}"
        f"{additional_info}"
        f"\n\n"
        f'\n{ICONS["special"]["app"]} <a href="{BOT_URL}/app">Приложение</a>'
        f'\n{ICONS["special"]["hashtags"]} <a href="{CHANNEL_URL}/5">Облако тэгов</a>'
        f"\n#{grenade.map.value} #{grenade.type.value} #{grenade.side.value}"
    )


async def create_grenade_post(ctx: dict, grenade_data: dict):
    admin_bot: Bot = Dependencies.admin_bot
    pyro_bot: PyrogramClient = Dependencies.pyro_bot
    grenade = GrenadeForWorker.model_validate(grenade_data)

    description = get_grenade_tg_post_text(grenade)

    aiogram_msg = await admin_bot.send_media_group(
        chat_id=CONFIG.cs_education_channel_id,
        media=[
            InputMediaVideo(media=grenade.tg_data.video_file_id, caption="Загрузка..."),
            InputMediaPhoto(media=grenade.tg_data.setup_photo_file_id),
            InputMediaPhoto(media=grenade.tg_data.finish_photo_file_id),
        ],
    )
    await asyncio.sleep(1)
    pyrogram_msg_id = await pyro_bot.ensure_edit_caption(
        text=description,
        chat_id=CONFIG.cs_education_channel_id,
        message_id=aiogram_msg[0].message_id,
    )
    logger.info(f"Сообщение ID: {pyrogram_msg_id} с гранатой ID {grenade.id} было отправлено")

    return CreateGrenadeJobResponse(
        tg_post_id=aiogram_msg[0].message_id,
        setup_photo_msg_id=aiogram_msg[1].message_id,
        finish_photo_msg_id=aiogram_msg[2].message_id,
    )
