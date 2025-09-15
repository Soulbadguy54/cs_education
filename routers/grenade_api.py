import logging
from typing import Annotated
from arq.jobs import SerializationError
from fastapi import APIRouter, Query, HTTPException, Body, Depends
from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import select, and_, delete
from starlette import status
from db.models import GrenadePublic, Grenade, NewGrenade, CsMaps, UserFavourite
from dependencies import SessionDep, QueueDep
from funcs.grenade_funcs import process_grenade_data
from funcs.key_builder import custom_key_builder
from funcs.objects import CreateGrenadeJobResponse
from funcs.user_funcs import get_current_admin, validate_token


logger = logging.getLogger("api_logger")
grenade_router = APIRouter(tags=["grenade"])


@grenade_router.get(
    path="/get",
    response_model=list[GrenadePublic],
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для получения всех гранат на заданной карте",
)
@cache(
    expire=60,
    namespace="get_grenades",
    coder=PickleCoder,
    key_builder=custom_key_builder,
)
async def get_grenades_endpoint(
    map_name: Annotated[CsMaps, Query()],
    session: SessionDep,
    user_id: Annotated[
        int, Query(description="ID пользователя для проверки избранного")
    ] = -1,
    current_admin: str = Depends(get_current_admin),
):
    stm = (
        select(Grenade, UserFavourite.date.is_not(None).label("_is_favourite"))
        .outerjoin(
            UserFavourite,
            and_(
                UserFavourite.grenade_id == Grenade.id, UserFavourite.user_id == user_id
            ),
        )
        .where(and_(Grenade.map == map_name.value, Grenade.tg_post_id.is_not(None)))
    )
    list_of_grenades = []
    for grenade_data in (await session.execute(stm)).all():
        grenade = GrenadePublic.model_validate(grenade_data[0])
        grenade.is_favourite = grenade_data[1]
        list_of_grenades.append(grenade)

    return list_of_grenades


@grenade_router.get(
    path="/get_grouped",
    response_model=dict[str, dict[int, GrenadePublic]],
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для получения всех гранат на заданной карте",
)
@cache(
    expire=60,
    namespace="get_grouped",
    coder=PickleCoder,
    key_builder=custom_key_builder,
)
async def get_grouped_grenades_endpoint(
    map_name: Annotated[CsMaps, Query()],
    session: SessionDep,
    user_id: Annotated[
        int, Query(description="ID пользователя для проверки избранного")
    ] = -1,
    current_token: str = Depends(validate_token),
):
    stm = (
        select(Grenade, UserFavourite.date.isnot(None).label("_is_favourite"))
        .outerjoin(
            UserFavourite,
            and_(
                UserFavourite.grenade_id == Grenade.id, UserFavourite.user_id == user_id
            ),
        )
        .where(and_(Grenade.map == map_name.value, Grenade.tg_post_id.is_not(None)))
    )

    dict_of_grenades: dict[str, dict[int, GrenadePublic]] = {}
    for grenade_data in (await session.execute(stm)).all():
        grenade = GrenadePublic.model_validate(grenade_data[0])
        grenade.is_favourite = grenade_data[1]

        key = f"{grenade.final_position.position.top}_{grenade.final_position.position.left}"
        dict_of_grenades.setdefault(key, {})[grenade.id] = grenade

    return dict_of_grenades


@grenade_router.post(
    path="/add",
    status_code=status.HTTP_201_CREATED,
    description="Эндпоинт для добавления гранаты",
    responses={
        201: {"description": "Граната успешно добавлена"},
        409: {"description": "Конфликт данных, нужно проверять ответ сервера"},
        422: {"description": "Ошибка валидации входных параметров"},
    },
)
async def add_grenade_endpoint(
    new_grenade: NewGrenade,
    session: SessionDep,
    queue: QueueDep,
    current_admin: str = Depends(get_current_admin),
):
    response_messages = []
    grenade = await process_grenade_data(new_grenade, session)
    response_messages.append(f'[+] Граната "{grenade.type.value}" [ID: {grenade.id}]')

    logger.info("Sending job [make_post] to worker...")
    dumped_model = grenade.model_dump(
        mode="json",
        include={
            "id",
            "type",
            "side",
            "difficult",
            "tg_post_id",
            "data",
            "tg_data",
            "map",
        },
    )
    dumped_model["initial_position"] = grenade.initial_position.model_dump(mode="json")
    dumped_model["final_position"] = grenade.final_position.model_dump(mode="json")
    dumped_model["key_combo"] = grenade.key_combo.model_dump(mode="json")

    job = await queue.enqueue_job(
        "create_grenade_post", dumped_model, _job_id=f"create_grenade_{grenade.id}"
    )
    try:
        job_data: CreateGrenadeJobResponse = await job.result(timeout=30)
        logger.info("Job [make_post] completed")
        response_messages.append(
            f"[+] Пост телеграм ID: [{job_data['tg_post_id']}] добавлен."
        )
    except SerializationError:
        await session.rollback()  # откатываем всё
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Граната [ID: {grenade.id}] не добавлена. Произошла ошибка при создании поста в телеграм",
        )

    grenade.tg_post_id = job_data["tg_post_id"]
    grenade.tg_data.setup_photo_msg_id = job_data["setup_photo_msg_id"]
    grenade.tg_data.finish_photo_msg_id = job_data["finish_photo_msg_id"]
    flag_modified(grenade, "tg_data")
    session.add(grenade)
    await session.commit()
    return {"message": " ".join(response_messages)}


@grenade_router.post(
    path="/edit",
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для изменения гранаты",
)
async def edit_grenade_endpoint(
    new_grenade: NewGrenade,
    session: SessionDep,
    queue: QueueDep,
    current_admin: str = Depends(get_current_admin),
):
    response_messages = []
    grenade = await process_grenade_data(new_grenade, session)
    response_messages.append(
        f'[o] Граната "{grenade.type.value}" [ID: {grenade.id}] обновлена.'
    )

    logger.info("Sending job [edit_post] to worker...")
    dumped_model = grenade.model_dump(
        mode="json",
        include={
            "id",
            "type",
            "side",
            "difficult",
            "tg_post_id",
            "data",
            "tg_data",
            "map",
        },
    )
    dumped_model["initial_position"] = grenade.initial_position.model_dump(mode="json")
    dumped_model["final_position"] = grenade.final_position.model_dump(mode="json")
    dumped_model["key_combo"] = grenade.key_combo.model_dump(mode="json")

    job = await queue.enqueue_job(
        "edit_grenade_post", dumped_model, _job_id=f"edit_grenade_{grenade.id}"
    )
    try:
        await job.result(timeout=30)
        logger.info("Job [edit_post] completed")
        response_messages.append(
            f"[o] Пост телеграм ID: [{grenade.tg_post_id}] измененён."
        )
    except SerializationError:
        await session.rollback()  # откатываем всё
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Граната [ID: {grenade.id}] не изменена. Произошла ошибка при редактировании поста в телеграм",
        )

    await session.commit()
    return {"message": " ".join(response_messages)}


@grenade_router.post(
    path="/add_to_favourite",
    status_code=status.HTTP_200_OK,
    description="Эндпоинт для добавления гранаты в избранное",
)
async def add_grenade_to_favourite(
    session: SessionDep,
    grenade_id: int = Body(...),
    user_id: int = Body(...),
    current_token: str = Depends(validate_token),
):
    try:
        stm = (
            insert(UserFavourite)
            .values(user_id=user_id, grenade_id=grenade_id)
            .on_conflict_do_nothing()
        )
        await session.execute(stm)
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="User_id or grenade_id not found",
        )

    return {
        "message": f"Grenade [ID: {grenade_id}] added to favourite for user [ID: {user_id}"
    }


@grenade_router.delete(
    path="/remove_from_favourite",
    status_code=status.HTTP_200_OK,
    description="Удаление из избранного",
)
async def endpoint_for_remove_from_favourite(
    grenade_id: Annotated[int, Query()],
    user_id: Annotated[int, Query()],
    session: SessionDep,
    current_token: str = Depends(validate_token),
):
    stm = delete(UserFavourite).where(
        and_(UserFavourite.grenade_id == grenade_id, UserFavourite.user_id == user_id)
    )
    await session.execute(stm)
    await session.commit()

    return {
        "message": f"Grenade [ID: {grenade_id}] removed from favourite for user [ID: {user_id}"
    }
