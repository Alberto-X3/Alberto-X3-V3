__all__ = (
    "BanModel",
    "KickModel",
)


from AlbertoX3.database import Base, UTCDatetime, db
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, Text


class BanModel(Base):
    __tablename__ = "ban"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    member: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    reason: Column | str = Column(Text(128), nullable=False)
    until: Column | datetime = Column(UTCDatetime, nullable=True)

    @staticmethod
    async def add(member: int, executor: int, reason: str, until: datetime | None) -> "BanModel":
        return await db.add(
            BanModel(
                member=member,
                executor=executor,
                timestamp=datetime.utcnow(),
                reason=reason,
                until=until,
            )
        )


class KickModel(Base):
    __tablename__ = "kick"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    member: Column | int = Column(BigInteger, nullable=False)
    executor: Column | int = Column(BigInteger, nullable=False)
    timestamp: Column | datetime = Column(UTCDatetime, nullable=False)
    reason: Column | str = Column(Text(128), nullable=False)

    @staticmethod
    async def add(member: int, executor: int, reason: str) -> "KickModel":
        return await db.add(
            KickModel(
                member=member,
                executor=executor,
                timestamp=datetime.utcnow(),
                reason=reason,
            )
        )
