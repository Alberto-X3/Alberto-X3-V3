from aenum import NoAliasEnum as aNoAliasEnum
from typing import TypeVar

T = TypeVar("T")

class NoAliasEnum(aNoAliasEnum):
    @property
    def extension(self) -> str: ...
    @property
    def fullname(self) -> str: ...
    @property
    def default(self) -> T: ...
