__all__ = ("CaseFileModel",)


from AlbertoX3.constants import MISSING
from AlbertoX3.database import Base, UTCDatetime, db
from datetime import datetime
from naff.client.const import EMBED_FIELD_VALUE_LENGTH
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer, Text


class CaseFileModel(Base):
    __tablename__ = "case_file"

    id: Column | int = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    author: Column | int = Column(BigInteger, nullable=False)
    created: Column | datetime = Column(UTCDatetime, nullable=False)
    last_edited: Column | datetime = Column(UTCDatetime, nullable=False)
    status: Column | int = Column(Integer, nullable=False)
    judge: Column | int = Column(BigInteger, nullable=False)
    lay_judge: Column | int | None = Column(BigInteger, nullable=True)
    complainant: Column | int = Column(BigInteger, nullable=False)
    complainant_lawyer: Column | int | None = Column(BigInteger, nullable=True)
    defendant: Column | int = Column(BigInteger, nullable=False)
    defendant_lawyer: Column | int | None = Column(BigInteger, nullable=True)
    witness: Column | int | None = Column(BigInteger, nullable=True)
    expert: Column | int | None = Column(BigInteger, nullable=True)
    accusation: Column | str = Column(Text(EMBED_FIELD_VALUE_LENGTH), nullable=False)

    @staticmethod
    def preview(
        author: int,
        status: int,
        judge: int,
        lay_judge: int | None,
        complainant: int,
        complainant_lawyer: int | None,
        defendant: int,
        defendant_lawyer: int | None,
        witness: int | None,
        expert: int | None,
        accusation: str,
    ) -> "CaseFileModel":
        return CaseFileModel(
            author=author,
            created=(utcnow := datetime.utcnow()),
            last_edited=utcnow,
            status=status,
            judge=judge,
            lay_judge=lay_judge,
            complainant=complainant,
            complainant_lawyer=complainant_lawyer,
            defendant=defendant,
            defendant_lawyer=defendant_lawyer,
            witness=witness,
            expert=expert,
            accusation=accusation,
        )

    @staticmethod
    async def create(
        author: int,
        status: int,
        judge: int,
        lay_judge: int | None,
        complainant: int,
        complainant_lawyer: int | None,
        defendant: int,
        defendant_lawyer: int | None,
        witness: int | None,
        expert: int | None,
        accusation: str,
    ) -> "CaseFileModel":
        return await db.add(CaseFileModel.preview(**locals()))

    @staticmethod
    async def get_by_id(id: int) -> "CaseFileModel | None":  # noqa A002
        return await db.get(CaseFileModel, id=id)

    @staticmethod
    async def get_last_recent_updated() -> "CaseFileModel":
        last_edited = await db.get(func.max(CaseFileModel.last_edited))
        return await db.get(CaseFileModel, last_edited=last_edited)

    async def edit(
        self,
        *,
        status: int = MISSING,
        judge: int = MISSING,
        lay_judge: int | None = MISSING,
        complainant: int = MISSING,
        complainant_lawyer: int | None = MISSING,
        defendant: int = MISSING,
        defendant_lawyer: int | None = MISSING,
        witness: int | None = MISSING,
        expert: int | None = MISSING,
        accusation: str = MISSING,
    ) -> "CaseFileModel":
        args = locals()
        args.pop("self")

        for name, value in args.items():
            if value is not MISSING:
                setattr(self, name, value)

        self.last_edited = datetime.utcnow()
        return self
