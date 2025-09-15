from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, model_validator
from sqlalchemy import (
    Column,
    UniqueConstraint,
    TypeDecorator,
    func,
    DateTime,
    BigInteger,
    ForeignKey,
    Integer,
    Boolean,
)
from sqlalchemy.dialects.postgresql import JSONB, CITEXT
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


class AppTheme(Enum):
    DARK = "dark"
    LIGHT = "light"


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
        filled_fields = sum(
            1 for x in [self.top, self.bottom, self.right, self.left] if x is not None
        )

        if filled_fields == 0:
            return self

        if filled_fields == 4:
            if self.top + self.bottom != 100:
                raise ValueError(
                    f"Сумма top ({self.top}) и bottom ({self.bottom}) должна быть 100, сейчас {self.top + self.bottom}"
                )
            if self.right + self.left != 100:
                raise ValueError(
                    f"Сумма right ({self.right}) и left ({self.left}) должна быть 100, сейчас {self.right + self.left}"
                )
            return self

        # Любое промежуточное состояние (1, 2 или 3 заполненных поля)
        raise ValueError(
            "Должны быть заданы все 4 поля (top, right, bottom, left) или ни одного. "
            f"Сейчас: top={self.top}, right={self.right}, bottom={self.bottom}, left={self.left}"
        )


class MapPositionBase(SQLModel):
    name: Optional[str] = None
    position: Optional[Position] = Field(sa_column=Column(PydanticJSONType(Position)), default=None)


class MapPosition(MapPositionBase, table=True):
    __tablename__ = "map_positions"
    __table_args__ = (
        UniqueConstraint("map", "position", name="unique_position"),
        {"schema": "public"},
    )

    id: int | None = Field(default=None, primary_key=True)
    map: CsMaps
    grenades_initial: list["Grenade"] = Relationship(
        back_populates="initial_position",
        sa_relationship_kwargs={"foreign_keys": "Grenade.initial_position_id"},
    )
    grenades_final: list["Grenade"] = Relationship(
        back_populates="final_position",
        sa_relationship_kwargs={"foreign_keys": "Grenade.final_position_id"},
    )


class MapPositionPublic(MapPositionBase):
    id: int


class NewMapPosition(MapPositionBase):
    id: Optional[int] = None
    map: Optional[CsMaps] = None

    @model_validator(mode="after")
    def check_consistency(self):
        if self.id and self.position:
            raise ValueError(
                "Нельзя передавать ID позиции и данные о позиции одновременно. Если необходимо создать новую позицию, "
                "то поле ID должно отсутствовать. Если необходимо изменить существующую позицию используй эндпоинт update"
            )

        return self


# ------------------------------------------------- KEY COMBINATIONS ---------------------------------------------------
class KeyCombo(SQLModel, table=True):
    __tablename__ = "key_combos"
    __table_args__ = {"schema": "public"}

    id: int | None = Field(default=None, primary_key=True)
    text: str = Field(sa_column=Column(CITEXT, unique=True))


class NewKeyCombo(BaseModel):
    id: int | None = None
    text: str | None = None

    @model_validator(mode="after")
    def check_consistency(self):
        if self.id and self.text:
            raise ValueError(
                "Нельзя передавать ID комбо и текст комбо одновременно. Если необходимо создать новое комбо, "
                "то поле ID должно отсутствовать. Если необходимо изменить существующее комбо используй эндпоинт update"
            )
        return self


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
        default=None, description="Время гранаты в полёте, в секундах"
    )
    additional_info: str | None = Field(
        default=None, description="Дополнительная инфа о гранате"
    )
    is_insta: bool = Field(default=False, description="Является ли граната инстантной")


class GrenadeBase(SQLModel):
    type: GrenadeType = Field(nullable=True)
    side: GrenadeSide = Field(nullable=True)
    difficult: int = Field(ge=1, le=3, nullable=True)
    data: GrenadeData = Field(sa_column=Column(PydanticJSONType(GrenadeData), nullable=True))

    class Config:
        use_enum_values = True


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
    tg_post_id: int | None = Field(default=None, index=True, nullable=True)
    tg_data: GrenadeTelegramData = Field(
        sa_column=Column(
            PydanticJSONType(GrenadeTelegramData),
            unique=True,
            nullable=True
        )
    )
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

    combo_id: int | None = Field(default=None, foreign_key="public.grenades_combo.id")
    combos: List["GrenadeCombo"] = Relationship(
        back_populates="grenades",
        link_model=ComboAndGrenadeLink,
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

    class Config:
        use_enum_values = True


class GrenadePublic(GrenadeBase):
    id: int
    initial_position: MapPositionPublic
    final_position: MapPositionPublic
    key_combo: KeyCombo
    tg_post_id: int
    is_favourite: bool = Field(default=False, description="Юзер добавил/удалил гранату в/из избранного")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime("%d.%m.%Y")
        }


class NewGrenade(GrenadeBase):
    id: int
    map: CsMaps
    initial_position: NewMapPosition
    final_position: NewMapPosition
    key_combo: NewKeyCombo

    class Config:
        use_enum_values = True


# -------------------------------------------------- USER TABLE --------------------------------------------------------
class UserChatData(BaseModel):
    user_ban_dt: Optional[int] = None


class UserData(BaseModel):
    language_code: str | None
    name: str | None


class UserBase(SQLModel):
    id: Optional[int] = Field(default=None)
    username: str | None = None
    user_data: UserData = Field(sa_column=Column(PydanticJSONType(UserData)))
    chat_data: UserChatData = Field(sa_column=Column(PydanticJSONType(UserChatData)))


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


class UserRawData(BaseModel):
    data: str


class NewUser(UserBase):
    id: Optional[int] = None
    username: str | None
    user_data: UserData
    invite_url: Optional[str] = Field(default=None)
    chat_data: Optional[UserChatData] = Field(default_factory=lambda: UserChatData(user_ban_dt=None))


# ------------------------------------------------- PYDANTIC ---------------------------------------------------------
class AdminDataResponse(BaseModel):
    map_positions: list[MapPositionPublic]
    key_combos: list[KeyCombo]


class DeleteQueryFilter(BaseModel):
    type: ItemType
    id: int


class EmptyResponse(BaseModel):
    pass
