import time
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, model_validator, computed_field
from sqlalchemy import (
    Column,
    UniqueConstraint,
    TypeDecorator,
    func,
    DateTime,
    BigInteger,
    Integer,
    ForeignKey,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import expression
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class GrenadeType(Enum):
    HE = "HE"
    FLASH = "FLASH"
    MOLOTOV = "MOLOTOV"
    SMOKE = "SMOKE"
    DECOY = "DECOY"


class GrenadeSide(Enum):
    CT = "CT"
    T = "T"


class CsMaps(Enum):
    ANCIENT = "ANCIENT"
    ANUBIS = "ANUBIS"
    CACHE = "CACHE"
    DUST2 = "DUST2"
    INFERNO = "INFERNO"
    MIRAGE = "MIRAGE"
    NUKE = "NUKE"
    OVERPASS = "OVERPASS"
    TRAIN = "TRAIN"
    VERTIGO = "VERTIGO"


class ItemType(str, Enum):
    GRENADE = "GRENADE"
    MAP_POSITION = "MAP_POSITION"
    KEY_COMBO = "KEY_COMBO"


class EnumTypesPublic(BaseModel):
    grenade_types: list[str]
    grenade_sides: list[str]
    maps: list[str]

    class Config:
        from_attributes = True


# Кастомный тип для сериализации/десериализации Pydantic в JSON
class PydanticJSONType(TypeDecorator):
    impl = JSONB
    cache_ok = True

    def __init__(self, pydantic_type):
        self.pydantic_type = pydantic_type
        super().__init__()

    def process_bind_param(self, value, dialect):
        """Преобразование объекта Pydantic в словарь для JSONB"""
        if isinstance(value, dict):
            return value
        elif value is None:
            return None
        else:
            return value.dict()  # type: ignore

    def process_result_value(self, value, dialect):
        """Преобразование JSON в объект Pydantic"""
        return self.pydantic_type(**value) if value else None


# -------------------------------------------------- LINK TABLES ------------------------------------------------------
class ComboAndGrenadeLink(SQLModel, table=True):
    __tablename__ = "combo_and_grenade_link"
    __table_args__ = {"schema": "public"}

    grenade_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("public.grenades.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    combo_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("public.grenades_combo.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


class UserFavourite(SQLModel, table=True):
    __tablename__ = "user_favourite"
    __table_args__ = {"schema": "public"}

    user_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("public.users.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    grenade_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("public.grenades.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    date: datetime = Field(default_factory=datetime.now, nullable=False, index=True)


# ------------------------------------------------- MAP POSITIONS -------------------------------------------------------
class Position(BaseModel):
    top: float | None = Field(ge=0, le=100)
    right: float | None = Field(ge=0, le=100)
    bottom: float | None = Field(ge=0, le=100)
    left: float | None = Field(ge=0, le=100)

    @model_validator(mode="after")
    def check_sums(self):
        filled_fields = sum(1 for x in [self.top, self.bottom, self.right, self.left] if x is not None)

        if filled_fields == 0:
            return self

        if filled_fields == 4:
            if self.top + self.bottom != 100:
                raise ValueError(
                    f"Sum of top ({self.top}) and bottom ({self.bottom}) must equal 100, got {self.top + self.bottom}"
                )
            if self.right + self.left != 100:
                raise ValueError(
                    f"Sum of right ({self.right}) and left ({self.left}) must equal 100, got {self.right + self.left}"
                )
            return self

        raise ValueError(
            "All fields (top, right, bottom, left) must either be fully filled or all None. "
            f"Current state: top={self.top}, right={self.right}, bottom={self.bottom}, left={self.left}"
        )


class MapPosition(SQLModel, table=True):
    __tablename__ = "map_positions"
    __table_args__ = (
        UniqueConstraint("map", "position", name="unique_position"),
        {"schema": "public"},
    )

    id: int | None = Field(default=None, primary_key=True)
    map: CsMaps
    name: str
    position: Position = Field(sa_column=Column(PydanticJSONType(Position)))
    grenades_initial: list["Grenade"] = Relationship(
        back_populates="initial_position",
        sa_relationship_kwargs={"foreign_keys": "Grenade.initial_position_id"},
    )
    grenades_final: list["Grenade"] = Relationship(
        back_populates="final_position",
        sa_relationship_kwargs={"foreign_keys": "Grenade.final_position_id"},
    )


# ------------------------------------------------- KEY COMBINATIONS ---------------------------------------------------
class KeyCombo(SQLModel, table=True):
    __tablename__ = "key_combos"
    __table_args__ = {"schema": "public"}

    id: int | None = Field(default=None, primary_key=True)
    text: str = Field(unique=True)


# ------------------------------------------------- GRENADES COMBO ------------------------------------------------------
class GrenadesComboBase(SQLModel):
    update_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime,
            default=func.now(),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
            index=True,
        ),
    )
    map: CsMaps
    side: GrenadeSide
    difficult: int
    position_id: int = Field(foreign_key="public.map_positions.id")
    data: Dict = Field(default_factory=dict, sa_column=Column(JSONB))


class GrenadeCombo(GrenadesComboBase, table=True):
    __tablename__ = "grenades_combo"
    __table_args__ = {"schema": "public"}

    id: int | None = Field(default=None, primary_key=True)
    grenades: list["Grenade"] = Relationship(back_populates="combos", link_model=ComboAndGrenadeLink)


class GrenadeComboPublic(GrenadesComboBase):
    id: int


# -------------------------------------------------- GRENADES ---------------------------------------------------------
class GrenadeTelegramData(BaseModel):
    video_file_id: str
    video_duration: int
    setup_photo_file_id: str
    finish_photo_file_id: str
    setup_photo_msg_id: int | None = None
    finish_photo_msg_id: int | None = None
    cover_file_id: str | None = None
    likes: int = Field(default=0)
    dislikes: int = Field(default=0)


class GrenadeData(BaseModel):
    best_timing: int | None = Field(
        default=None,
        description="Время в секундах от начала раунда, например 12 секунд",
    )
    time_in_fly: int | None = Field(
        default=None,
        description="Время гранаты в полёте, в секундах"
    )
    additional_info: str | None = Field(
        default=None,
        description="Дополнительная инфа о гранате"
    )
    is_insta: bool  # insta grenade or not


class GrenadeBase(SQLModel):
    type: GrenadeType = Field(nullable=True)
    side: GrenadeSide = Field(nullable=True)
    difficult: int = Field(ge=1, le=3, nullable=True)
    tg_post_id: int | None = Field(default=None, index=True, nullable=True)
    data: GrenadeData = Field(sa_column=Column(PydanticJSONType(GrenadeData), nullable=True)
    )


class Grenade(GrenadeBase, table=True):
    __tablename__ = "grenades"
    __table_args__ = (
        UniqueConstraint(
            "map",
            "initial_position_id",
            "final_position_id",
            "type",
            name="unique_grenade_data",
        ),
        {"schema": "public"},
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    update_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime,
            default=func.now(),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
            index=True,
        ),
    )
    map: CsMaps = Field(nullable=True)
    key_combo_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("public.key_combos.id", ondelete="CASCADE"),
            nullable=True,
        )
    )
    initial_position_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("public.map_positions.id", ondelete="CASCADE"),
            nullable=True,
        )
    )
    final_position_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("public.map_positions.id", ondelete="CASCADE"),
            nullable=True,
        )
    )
    tg_data: GrenadeTelegramData = Field(
        sa_column=Column(
            PydanticJSONType(GrenadeTelegramData),
            unique=True,
            nullable=True
        )
    )

    combo_id: int | None = Field(default=None, foreign_key="public.grenades_combo.id")
    combos: List["GrenadeCombo"] = Relationship(
        back_populates="grenades",
        link_model=ComboAndGrenadeLink
    )

    initial_position: MapPosition = Relationship(
        back_populates="grenades_initial",
        sa_relationship_kwargs={
            "foreign_keys": "Grenade.initial_position_id",
            "lazy": "joined",
        },
    )
    final_position: MapPosition = Relationship(
        back_populates="grenades_final",
        sa_relationship_kwargs={
            "foreign_keys": "Grenade.final_position_id",
            "lazy": "joined",
        },
    )
    key_combo: KeyCombo = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "Grenade.key_combo_id",
            "lazy": "joined",
        }
    )


class GrenadeForWorker(GrenadeBase):
    id: int
    initial_position: MapPosition
    final_position: MapPosition
    key_combo: KeyCombo
    tg_data: GrenadeTelegramData
    map: CsMaps


# -------------------------------------------------- USER TABLE --------------------------------------------------------
class UserAppData(BaseModel):
    last_homescreen_alert: int | None = None
    last_enter: int | None = None
    timeout: bool = False


class UserChatData(BaseModel):
    user_ban_dt: Optional[int] = None


class UserData(BaseModel):
    language_code: str | None
    name: str | None


class UserBase(SQLModel):
    id: Optional[int] = Field(default=None)
    username: str | None = None
    user_data: UserData = Field(
        default_factory=lambda: UserData(language_code=None, name=None),
        sa_column=Column(PydanticJSONType(UserData)),
    )
    chat_data: UserChatData = Field(
        default_factory=lambda: UserChatData(user_ban_dt=None),
        sa_column=Column(PydanticJSONType(UserChatData)),
    )
    app_data: UserAppData = Field(
        default_factory=lambda: UserAppData(
            last_homescreen_alert=None,
            last_enter=None,
            timeout=False,
        ),
        sa_column=Column(PydanticJSONType(UserAppData)),
    )


class User(UserBase, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id: int = Field(primary_key=True, sa_type=BigInteger)
    date: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.now(),
            nullable=False
        )
    )
    invite_url: Optional[str] = Field(default=None)
    is_subscribed: bool = Field(
        sa_column=Column(
            Boolean,
            server_default=expression.false(),
            nullable=False
        )
    )


# Модель для ответа
class UserPublicApp(UserBase):
    @computed_field
    def show_homescreen_alert(self) -> bool:
        if self.app_data.last_enter is None:
            return False

        if self.app_data.last_homescreen_alert is None:
            return True

        difference_required: int | None = 60 * 60 * 24  # 1 день
        if self.app_data.timeout is True:
            difference_required *= 7  # неделя

        time_difference = int(time.time()) - self.app_data.last_homescreen_alert
        if time_difference >= difference_required:
            return True

        return False


class NewUser(UserBase):
    id: Optional[int] = None
    username: str | None
    user_data: UserData
    chat_data: Optional[UserChatData] = Field(
        default_factory=lambda: UserChatData(user_ban_dt=None)
    )
    app_data: Optional[UserAppData] = Field(
        default_factory=lambda: UserAppData(
            last_homescreen_alert=None,
            block_homescreen_alert=False,
            last_enter=None
        )
    )
