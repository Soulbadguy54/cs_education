import logging
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from sqlmodel import select
from starlette import status
from config import CONFIG
from db.models import (
    AdminDataResponse,
    CsMaps,
    MapPosition,
    KeyCombo,
    EnumTypesPublic,
    GrenadeType,
    GrenadeSide,
)
from dependencies import SessionDep
from funcs.user_funcs import verify_password, create_access_token, get_current_admin


logger = logging.getLogger("api_logger")
admin_router = APIRouter(tags=["admin"])


ADMIN_CONFIG = CONFIG.admin_data
ACCESS_TOKEN_EXPIRE_MINUTES = 360


# Эндпоинт для получения токена
@admin_router.post("/get_token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_CONFIG.username or not verify_password(
        form_data.password, ADMIN_CONFIG.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"keyword": ADMIN_CONFIG.username},
        ADMIN_CONFIG.secret_key,
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@admin_router.get(
    path="/get_data",
    response_model=AdminDataResponse,
    status_code=status.HTTP_200_OK,
    description="Возвращает список всех позиций на карте и комбинаций клавиш",
)
async def return_admin_data(
    map_name: Annotated[CsMaps, Query()],
    session: SessionDep,
    current_admin: str = Depends(get_current_admin),
):
    stm = (
        select(MapPosition)
        .where(MapPosition.map == map_name.value)
    )
    map_positions = (await session.execute(stm)).scalars().all()

    key_combos = (await session.execute(select(KeyCombo))).scalars().all()

    return AdminDataResponse(map_positions=map_positions, key_combos=key_combos)


@admin_router.get(
    path="/enums",
    response_model=EnumTypesPublic,
    status_code=status.HTTP_200_OK,
    description="Возвращает возможные значения для перечислений, используемых в API",
)
@cache(expire=43200, namespace="enums")  # 12 часов
async def return_enum_values(current_admin: str = Depends(get_current_admin)):
    return EnumTypesPublic(
        grenade_types=[item.value for item in GrenadeType],
        grenade_sides=[item.value for item in GrenadeSide],
        maps=[item.value for item in CsMaps],
    )
