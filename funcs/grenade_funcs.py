import logging
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import update, delete
from starlette import status
from db.models import (
    NewGrenade,
    Grenade,
    NewMapPosition,
    MapPosition,
    NewKeyCombo,
    KeyCombo,
)


async def add_map_position(new_map_position: NewMapPosition, session: AsyncSession) -> int:
    if not all(
        (
            new_map_position.map,
            new_map_position.position,
            new_map_position.name,
        )
    ):
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=f"Не хватает полей в map_position. map: {new_map_position.map}, "
                   f"position: {new_map_position.position}, name: {new_map_position.name}",
        )

    map_position = MapPosition.model_validate(new_map_position)
    try:
        session.add(map_position)
        await session.flush()
        return map_position.id
    except IntegrityError as e:
        await session.rollback()
        logging.error(e.orig.__repr__())
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
        # detail=e.orig.__repr__().split(': ', 1)[1].strip(".')"))


async def update_map_position(map_position: MapPosition, session: AsyncSession) -> int:
    stm = (
        update(MapPosition)
        .values(map_position.model_dump(exclude_none=True))
        .where(MapPosition.id == map_position.id)
        .returning(MapPosition.id)
    )
    map_position_id = (await session.execute(stm)).scalar()

    if not map_position_id:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=f"Map position [ID: {map_position_id} не найдена",
        )

    return map_position_id


async def delete_map_position(map_position_id: int, session: AsyncSession) -> int:
    stm = (
        delete(MapPosition)
        .where(MapPosition.id == map_position_id)
        .returning(MapPosition.id)
    )
    map_position_id = (await session.execute(stm)).scalar()
    if not map_position_id:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=f"Map position [ID: {map_position_id} не найдена",
        )

    return map_position_id


async def add_key_combo(new_key_combo: NewKeyCombo, session: AsyncSession) -> int:
    key_combo = KeyCombo.model_validate(new_key_combo)

    try:
        session.add(key_combo)
        await session.flush()
        return key_combo.id
    except IntegrityError as e:
        await session.rollback()
        logging.error(e.orig.__repr__())
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )


async def update_key_combo(key_combo: KeyCombo, session: AsyncSession) -> int:
    stm = (
        update(KeyCombo)
        .values(key_combo.model_dump(exclude_none=True))
        .where(KeyCombo.id == key_combo.id)
        .returning(KeyCombo.id)
    )
    key_combo_id = (await session.execute(stm)).scalar()

    if not key_combo_id:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=f"Key combo [ID: {key_combo_id} не найдено",
        )

    return key_combo_id


async def delete_key_combo(key_combo_id: int, session: AsyncSession) -> int:
    stm = (
        delete(KeyCombo)
        .where(KeyCombo.id == key_combo_id)
        .returning(KeyCombo.id)
    )
    key_combo_id = (await session.execute(stm)).scalar()

    if not key_combo_id:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=f"Key combo [ID: {key_combo_id} не найдено",
        )

    return key_combo_id


async def process_grenade_data(new_grenade: NewGrenade, session: AsyncSession) -> Grenade | None:
    response_messages = []
    if not new_grenade.initial_position.id:
        new_grenade.initial_position.map = new_grenade.map
        initial_position_id = await add_map_position(new_grenade.initial_position, session)

        response_messages.append(f'[+] Новая позиция "{new_grenade.initial_position.name} [ID: {initial_position_id}]')
    else:
        initial_position_id = new_grenade.initial_position.id

    if not new_grenade.final_position.id:
        new_grenade.final_position.map = new_grenade.map
        final_position_id = await add_map_position(new_grenade.final_position, session)
        response_messages.append(f'[+] Новая позиция "{new_grenade.final_position.name} [ID: {final_position_id}]')
    else:
        final_position_id = new_grenade.final_position.id

    if not new_grenade.key_combo.id:
        key_combo_id = await add_key_combo(new_grenade.key_combo, session)
        response_messages.append(f'[+] Новая комбинация клавиш "{new_grenade.key_combo.text}" [ID: {key_combo_id}]')
    else:
        key_combo_id = new_grenade.key_combo.id

    return await add_or_update_grenade(
        new_grenade=new_grenade,
        initial_position_id=initial_position_id,
        final_position_id=final_position_id,
        key_combo_id=key_combo_id,
        session=session,
    )


async def add_or_update_grenade(
    new_grenade: NewGrenade,
    initial_position_id: int,
    final_position_id: int,
    key_combo_id: int,
    session: AsyncSession,
) -> Grenade | None:
    grenade_dumped = new_grenade.model_dump(
        exclude={"initial_position", "final_position", "key_combo", "id"}
    )
    grenade_dumped.update(
        initial_position_id=initial_position_id,
        final_position_id=final_position_id,
        key_combo_id=key_combo_id,
    )

    stm = (
        update(Grenade)
        .values(grenade_dumped)
        .where(Grenade.id == new_grenade.id)
        .returning(Grenade.id)
    )
    grenade_id = (await session.execute(stm)).scalar()

    if not grenade_id:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Grenade [ID: {grenade_id} not found",
        )
    await session.flush()

    grenade = await session.get(Grenade, grenade_id)
    return grenade
