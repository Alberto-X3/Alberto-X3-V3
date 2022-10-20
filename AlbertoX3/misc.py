__all__ = (
    "FormatStr",
    "PrimitiveExtension",
)


from pathlib import Path
from typing import Callable


class FormatStr(str):
    __call__: Callable[..., str] = str.format


class PrimitiveExtension:
    name: str
    package: str
    path: Path

    def __init__(self, name: str, package: str, path: Path):
        self.name = name
        self.package = package
        self.path = path

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({self.name!r} at {self.path})>"

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} {self.name!r}>"
