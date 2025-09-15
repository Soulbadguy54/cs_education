import asyncio
import logging
import traceback
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import BadRequest, FloodWait
from pyrogram.types import LinkPreviewOptions


class PyrogramClient(Client):
    async def ensure_send_message(
        self,
        text: str,
        chat_id: int,
        disable_notification: bool = False
    ) -> int | None:
        try:
            msg = await self.send_message(
                text=text,
                chat_id=chat_id,
                disable_notification=disable_notification
            )
            return msg.id
        except FloodWait as e:
            logging.info(f"ERROR FLOODWAIT: {e.args}")
            wait_seconds = int(e.args[0].split("wait of ", 1)[1].split(" seconds")[0])
            await asyncio.sleep(wait_seconds + 1)
            return await self.ensure_send_message(text, chat_id, disable_notification)
        except Exception as e:
            logging.error("".join(traceback.TracebackException.from_exception(e).format()))
            return

    async def ensure_edit_text_message(
        self,
        text: str,
        chat_id: int,
        message_id: int
    ) -> int | None:
        try:
            msg = await self.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=message_id
            )
            return msg.id
        except BadRequest:
            pass
        except FloodWait as e:
            logging.info(f"ERROR FLOODWAIT: {e.args}")
            wait_seconds = int(e.args[0].split("wait of ", 1)[1].split(" seconds")[0])
            await asyncio.sleep(wait_seconds + 1)
            return await self.ensure_edit_text_message(text, chat_id, message_id)
        except Exception as e:
            logging.error("".join(traceback.TracebackException.from_exception(e).format()))

    async def ensure_edit_caption(
        self,
        text: str,
        chat_id: int,
        message_id: int
    ) -> int | None:
        try:
            msg = await self.edit_message_caption(
                caption=text,
                chat_id=chat_id,
                message_id=message_id
            )
            return msg.id
        except BadRequest:
            pass
        except FloodWait as e:
            logging.info(f"ERROR FLOODWAIT: {e.args}")
            wait_seconds = int(e.args[0].split("wait of ", 1)[1].split(" seconds")[0])
            await asyncio.sleep(wait_seconds + 1)
            return await self.ensure_edit_caption(text, chat_id, message_id)
        except Exception as e:
            logging.error("".join(traceback.TracebackException.from_exception(e).format()))


pyro_bot = PyrogramClient(
    "cs_education",
    skip_updates=True,
    no_updates=True,
    parse_mode=ParseMode.HTML,
    no_joined_notifications=True,
    link_preview_options=LinkPreviewOptions(is_disabled=True),
)
