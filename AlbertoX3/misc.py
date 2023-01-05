__all__ = (
    "FormatStr",
    "EXTENSION_FEATURES",
    "PrimitiveExtension",
)


from naff.client.const import MISSING
from pathlib import Path
from typing import Callable, Iterable, Literal


class FormatStr(str):
    __call__: Callable[..., str] = str.format


_EXTENSION_FEATURES = Literal["colors", "db", "ext", "permissions", "settings", "stats"]

# only public because this might be of interest and not in .constants since it's required in here
EXTENSION_FEATURES: tuple[_EXTENSION_FEATURES] = _EXTENSION_FEATURES.__args__  # type: ignore


class PrimitiveExtension:
    name: str
    package: str
    path: Path
    features: int

    def __init__(self, name: str, package: str, path: Path, *, has: Iterable[_EXTENSION_FEATURES] = MISSING):
        self.name = name
        self.package = package
        self.path = path

        self.features = 0
        if has is not MISSING:
            for i, feature in enumerate(EXTENSION_FEATURES):
                if feature not in has:
                    continue
                self.features += 1 << i

    @property
    def has_colors(self) -> bool:
        """
        Whether it features a colors.py-file or not.
        """
        return self._has(0)

    @property
    def has_db(self) -> bool:
        """
        Whether it features a db.py-file or not.
        """
        return self._has(1)

    @property
    def has_ext(self) -> bool:
        """
        Whether it features an ext.py-file or not.
        """
        return self._has(2)

    @property
    def has_permission(self) -> bool:
        """
        Whether it features a permission.py-file or not.
        """
        return self._has(3)

    @property
    def has_settings(self) -> bool:
        """
        Whether it features a settings.py-file or not.
        """
        return self._has(4)

    @property
    def has_stats(self) -> bool:
        """
        Whether it features a stats.py-file or not.
        """
        return self._has(5)

    def _has(self, i: int) -> bool:
        return (self.features & (1 << i)) == (1 << i)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name!r} ({self.features})>"
