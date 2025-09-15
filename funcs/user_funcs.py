import hashlib
import hmac
import json
from copy import deepcopy
from datetime import timedelta, datetime, timezone
from operator import itemgetter
from typing import Optional, Any
from urllib.parse import parse_qsl
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlmodel import col
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from config import CONFIG
from db.models import NewUser, User


ADMIN_CONFIG = CONFIG.admin_data
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def add_or_update_user(new_user: NewUser, session: AsyncSession) -> bool:
    user_dumped = new_user.model_dump()
    data_for_update = deepcopy(user_dumped)
    del data_for_update["chat_data"]
    del data_for_update["invite_url"]

    try:
        stm = (
            insert(User)
            .values(**user_dumped)
            .on_conflict_do_update(index_elements=[col(User.id)], set_=data_for_update)
            .returning(User.is_subscribed)
        )
        is_subscribed = (await session.execute(stm)).scalar()
        return is_subscribed
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.orig.__repr__().split(": ", 1)[1].strip(".')"),
        )


def check_webapp_signature(token: str, data: str) -> bool:
    try:
        parsed_data = dict(parse_qsl(data, strict_parsing=True))
    except ValueError:
        return False
    if "hash" not in parsed_data:
        return False
    hash_ = parsed_data.pop("hash")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=token.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = (
        hmac.new(
            key=secret_key.digest(),
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256,
        )
        .hexdigest()
    )
    return calculated_hash == hash_


def parse_webapp_init_data(data: str) -> dict[str, Any]:
    result = {}
    for key, value in parse_qsl(data):
        if (value.startswith("[") and value.endswith("]")) or (value.startswith("{") and value.endswith("}")):
            value = json.loads(value)
        result[key] = value
    return result


# Верификация пароля
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Создание JWT-токена
def create_access_token(data: dict, key: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key, algorithm=ALGORITHM)
    return encoded_jwt


# Получение текущего администратора по токену
async def get_current_admin(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ADMIN_CONFIG.secret_key, algorithms=ALGORITHM)
        username: str = payload.get("keyword")
        if username != ADMIN_CONFIG.username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username


async def validate_token(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, CONFIG.bot_token, algorithms=ALGORITHM)
        if payload.get("keyword") != "regular":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return token
