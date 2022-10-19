from pathlib import Path
from typing import Callable

class FormatStr(str):
    __call__: Callable[..., str]  # see str.format

class PrimitiveExtension:
    name: str
    package: str
    path: Path
    def __init__(self, name: str, package: str, path: Path): ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
