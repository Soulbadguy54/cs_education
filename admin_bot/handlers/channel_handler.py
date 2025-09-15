import logging
from copy import deepcopy
from datetime import datetime
from aiogram import Router, F
from aiogram.types import (
    MessageReactionCountUpdated,
    ReactionTypePaid,
    ChatMemberUpdated,
    ReactionTypeCustomEmoji,
)
from sqlalchemy.dialects.postgresql import insert
from config import CONFIG
from database.models import Grenade, User
from tools.deps import Dependencies
from sqlmodel import update, col


logger = logging.getLogger("lifespan")

channel_router = Router(name="channel")
channel_router.message_reaction_count.filter(
    F.chat.id == CONFIG.cs_education_channel_id
)
# channel_router.channel_post.filter(F.chat.id == CONFIG.cs_education_channel_id)


@channel_router.message_reaction_count()
async def count_reactions(message_reaction_count: MessageReactionCountUpdated):
    msg_id = message_reaction_count.message_id
    likes, dislikes = 0, 0

    for reaction in message_reaction_count.reactions:
        if isinstance(reaction.type, ReactionTypePaid):
            emoji_identifier = "🔥"
        elif isinstance(reaction.type, ReactionTypeCustomEmoji):
            emoji_identifier = str(reaction.type.custom_emoji_id)
        elif reaction.type.emoji:
            emoji_identifier = reaction.type.emoji
        else:
            continue

        match emoji_identifier:
            case "💩" | "5262651280651748902":
                dislikes += reaction.total_count
            case "🔥" | "5262736918004659922" | "5262982542889354094":
                likes += reaction.total_count

    async with Dependencies.db_pool() as session:
        stm = (
            update(Grenade)
            .values(tg_data=Grenade.tg_data + {"likes": likes, "dislikes": dislikes})
            .where(Grenade.tg_post_id == msg_id)
        )
        await session.execute(stm)
        await session.commit()


@channel_router.chat_member()
async def process_chat_member(chat_member: ChatMemberUpdated):
    async with Dependencies.db_pool() as session:
        match chat_member.new_chat_member.status:
            case "member":
                user_data = {
                    "id": chat_member.from_user.id,
                    "username": chat_member.from_user.username,
                    "user_data": {
                        "name": chat_member.from_user.full_name,
                        "language_code": chat_member.from_user.language_code,
                    },
                    "chat_data": {"user_ban_dt": None},
                    "invite_url": chat_member.invite_link.invite_link.rsplit("/", 1)[-1]
                    if chat_member.invite_link
                    else None,
                    "is_subscribed": True,
                    "date": datetime.now(),
                }
                data_for_update = deepcopy(user_data)
                del data_for_update["chat_data"]
                del data_for_update["invite_url"]

                stm = (
                    insert(User)
                    .values(**user_data)
                    .on_conflict_do_update(
                        index_elements=[col(User.id)], set_=data_for_update
                    )
                )
                await session.execute(stm)
            case "left" | "kicked":
                user_data = {
                    "is_subscribed": False,
                    "date": datetime.now(),
                }
                stm = (
                    update(User)
                    .values(**user_data)
                    .where(User.id == chat_member.from_user.id)
                )
                await session.execute(stm)
        await session.commit()
