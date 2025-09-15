import logging
from datetime import timedelta
from fastapi import APIRouter, HTTPException
from starlette import status
from config import CONFIG
from db.models import NewUser, UserRawData, UserData
from dependencies import SessionDep
from funcs.user_funcs import (
    add_or_update_user,
    check_webapp_signature,
    parse_webapp_init_data,
    create_access_token,
)


logger = logging.getLogger("api_logger")
user_router = APIRouter(tags=["user"])

ACCESS_TOKEN_EXPIRE_MINUTES = 1440


@user_router.post(
    path="/update",
    status_code=status.HTTP_201_CREATED,
    description="Эндпоинт для добавления и обновления юзера",
)
async def create_or_update_user(data: UserRawData, session: SessionDep):
    if not check_webapp_signature(CONFIG.bot_token, data.data):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Несанкционированный доступ",
        )

    user_data = parse_webapp_init_data(data.data)
    is_subscribed = await add_or_update_user(
        new_user=NewUser(
            id=user_data["user"]["id"],
            username=user_data["user"].get("username"),
            user_data=UserData(
                language_code=user_data["user"].get("language_code"),
                name=user_data["user"].get("first_name", "") + " " + user_data["user"].get("last_name", ""),
            ),
            invite_url=user_data.get("start_param"),
        ),
        session=session,
    )
    await session.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"keyword": "regular"},
        CONFIG.bot_token,
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_subscribed": is_subscribed,
    }
