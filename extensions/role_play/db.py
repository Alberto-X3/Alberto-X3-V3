__all__ = ("FileCaseModel",)


from AlbertoX3.constants import MISSING
from AlbertoX3.database import Base, UTCDatetime, db
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, Text, func


class FileCaseModel(Base):
    __tablename__ = "file_case"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    author: Column | int = Column(BigInteger, nullable=False)
    created: Column | datetime = Column(UTCDatetime, nullable=False)
    last_edited: Column | datetime = Column(UTCDatetime, nullable=False)
    judge: Column | int = Column(BigInteger, nullable=False)
    complainant: Column | int = Column(BigInteger, nullable=False)
    defendant: Column | int = Column(BigInteger, nullable=False)
    appeal: Column | str = Column(Text(512), nullable=False)

    @staticmethod
    async def create(author: int, judge: int, complainant: int, defendant: int, appeal: str) -> "FileCaseModel":
        return await db.add(
            FileCaseModel(
                author=author,
                created=(utcnow := datetime.utcnow()),
                last_edited=utcnow,
                judge=judge,
                complainant=complainant,
                defendant=defendant,
                appeal=appeal,
            )
        )

    @staticmethod
    async def get_by_id(id: int) -> "FileCaseModel | None":  # noqa A002
        return await db.get(FileCaseModel, id=id)

    @staticmethod
    async def get_last_recent_updated() -> "FileCaseModel":
        return await db.get(FileCaseModel, FileCaseModel.last_edited == func.max(FileCaseModel.last_edited))

    async def edit(
        self, *, judge: int = MISSING, complainant: int = MISSING, defendant: int = MISSING, appeal: str = MISSING
    ) -> "FileCaseModel":
        if judge is not MISSING:
            self.judge = judge
        if complainant is not MISSING:
            self.complainant = complainant
        if defendant is not MISSING:
            self.defendant = defendant
        if appeal is not MISSING:
            self.appeal = appeal
        self.last_edited = datetime.utcnow()
        return self
