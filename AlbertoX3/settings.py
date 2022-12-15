__all__ = (
    "SettingsModel",
    "Settings",
    "RoleSettings",
)


import sys
from aenum import NoAliasEnum
from sqlalchemy import Column, String, Text
from .aio import LockDeco
from .database import Base, db, redis
from .environment import CACHE_TTL


_VALUE = str | int | float | bool


class SettingsModel(Base):
    __tablename__ = "settings"

    key: str | Column = Column(String(64), primary_key=True, unique=True)
    value: str | Column = Column(Text(256))

    @staticmethod
    async def _create(key: str, value: _VALUE) -> "SettingsModel":
        return await db.add(SettingsModel(key=key, value=str(int(value) if isinstance(value, bool) else value)))

    @staticmethod
    @LockDeco
    async def get(dtype: type[_VALUE], key: str, default: _VALUE) -> _VALUE:
        if (out := await redis.get(rkey := f"settings:{key}")) is None:
            if (row := await db.get(SettingsModel, key=key)) is None:
                row = await SettingsModel._create(key, default)
            out = row.value
            await redis.setex(rkey, CACHE_TTL, out)

        return dtype(int(out) if dtype is bool else out)

    @staticmethod
    @LockDeco
    async def set(dtype: type[_VALUE], key: str, value: _VALUE) -> "SettingsModel":  # noqa A003
        rkey = f"settings:{key}"
        if (row := await db.get(SettingsModel, key=key)) is None:
            row = await SettingsModel._create(key, value)
            await redis.setex(rkey, CACHE_TTL, row.value)
            return row

        row.value = str(int(value) if dtype is bool else value)
        await redis.setex(rkey, CACHE_TTL, row.value)
        return row


class Settings(NoAliasEnum):
    @property
    def ext(self) -> str:
        return sys.modules[self.__class__.__module__].__package__.rsplit(".", maxsplit=1)[-1]

    @property
    def fullname(self) -> str:
        return "{0.ext}.{0.name}".format(self)

    @property
    def default(self) -> _VALUE:
        return self.value

    @property
    def type(self) -> type[_VALUE]:  # noqa A003
        return type(self.default)

    async def get(self) -> _VALUE:
        return await SettingsModel.get(self.type, self.fullname, self.default)

    async def set(self, value: _VALUE) -> _VALUE:  # noqa A003
        await SettingsModel.set(self.type, self.fullname, value)
        return value

    async def reset(self) -> _VALUE:
        return await self.set(self.default)


class RoleSettings:
    @staticmethod
    async def get(name: str) -> int:
        return await SettingsModel.get(int, f"role:{name}", -1)

    @staticmethod
    async def set(name: str, role_id: int) -> int:  # noqa A003
        await SettingsModel.set(int, f"role:{name}", role_id)
        return role_id
