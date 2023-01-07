__all__ = (
    "MaintenanceUsersModel",
    "MaintenanceRolesModel",
)


from AlbertoX3.database import Base, db, filter_by
from naff.client.client import Client
from naff.models.discord.guild import Guild
from naff.models.discord.role import Role
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger


class MaintenanceUsersModel(Base):
    __tablename__ = "maintenance_users"

    user: Column | int = Column(BigInteger, primary_key=True, unique=True, autoincrement=False, nullable=False)
    roles: Column | int = Column(BigInteger, nullable=False)
    guild: Column | int = Column(BigInteger, nullable=False)

    async def get_discord_roles(self, client: Client) -> set[Role]:
        guild: Guild = await client.fetch_guild(self.guild)  # type: ignore
        roles: set[Role] = set()
        for role in range(self.roles.bit_length()):
            if (self.roles & (1 << role)) == (1 << role):
                roles.add(await guild.fetch_role((await MaintenanceRolesModel.get(role)).role))  # type: ignore
        return roles

    @staticmethod
    async def add(user: int, roles: int, guild: int) -> "MaintenanceUsersModel":
        return await db.add(MaintenanceUsersModel(user=user, roles=roles, guild=guild))

    @staticmethod
    async def get(user: int) -> "MaintenanceUsersModel":
        return await db.get(MaintenanceUsersModel, user=user)

    @staticmethod
    async def clear() -> None:
        await clear(MaintenanceUsersModel)


class MaintenanceRolesModel(Base):
    __tablename__ = "maintenance_roles"

    id: Column | int = Column(BigInteger, primary_key=True, unique=True, autoincrement=False, nullable=False)
    role: Column | int = Column(BigInteger, nullable=False)

    @staticmethod
    async def add(id: int, role: int) -> "MaintenanceRolesModel":  # noqa A002
        return await db.add(MaintenanceRolesModel(id=id, role=role))

    @staticmethod
    async def get(id: int) -> "MaintenanceRolesModel":  # noqa A002
        return await db.get(MaintenanceRolesModel, id=id)

    @staticmethod
    async def clear() -> None:
        await clear(MaintenanceRolesModel)


async def clear(model: type[Base]) -> None:
    async for row in await db.stream(filter_by(model)):
        await db.delete(row)
