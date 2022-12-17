"""
This file only contains essential contents from "./utils.py".
It was created to avoid circular imports inside AlbertoX3 itself.

**Everything in here is considered part of "AlbertoX3.utils"!**
"""


__all__ = (
    "get_logger",
    "get_bool",
)


from AlbertUnruhUtils.utils.logger import (
    get_logger as auu_get_logger,
    _LOG_LEVEL_STR,  # noqa (_LOG_LEVEL_STR is not in __all__)
)
from logging import Logger
from typing import Optional, TypeVar, Callable, ParamSpec
from .errors import UnrecognisedBooleanError


# only used for metadata
_T = TypeVar("_T")
_P = ParamSpec("_P")
_FUNC = Callable[_P, _T]


def _utils(func: _FUNC) -> _FUNC:
    func.__module__ = f"{__package__}.utils"
    return func


@_utils
def get_logger(name: str, level: Optional[_LOG_LEVEL_STR | int] = None) -> Logger:
    """
    Gets a logger.

    Notes
    -----
    You should only pass a hardcoded name for ``name`` or use ``__name__``.
    Noteworthy is that any names containing a "." (dot) will be modified.

    Parameters
    ----------
    name: str
        The loggers name. (Set a name or use ``__name__``/``__package__`` in any extension or ``__name__``)
    level: _LOG_LEVEL_STR, int, optional
        The loglevel for the logger.

    Returns
    -------
    Logger
        The created logger.
    """
    if "." in name:
        parts = name.split(".")
        match len(parts):
            case 2:  # __package__ from an ext/__name__ from AlbertoX3.*-file
                name = parts[1]
            case 3:  # __name__ from an ext
                name = parts[1]

    return auu_get_logger(name=name, level=level, add_handler=False)


@_utils
def get_bool(obj: object, /) -> bool:
    """
    Currently matches:
        - True -> boolean, 1, lowered("true", "t", "yes", "y"), "1"
        - False -> boolean, -1, 0, lowered("false", "f", "no", "n"), "-1", "0"

    Parameters
    ----------
    obj: object
        The object to match (should be bool, int or str; others aren't supported at the moment)

    Returns
    -------
    bool
        The matched boolean.

    Raises
    ------
    UnrecognisedBooleanError
        Raised when the object couldn't be matched to a boolean.
    """
    match obj:
        case bool():
            return obj  # type: ignore
        case int():
            match obj:
                case 1:
                    return True
                case -1 | 0:
                    return False
        case str():
            match obj.lower():  # type: ignore
                case "true" | "t" | "yes" | "y" | "1":
                    return True
                case "false" | "f" | "no" | "n" | "-1" | "0":
                    return False
    raise UnrecognisedBooleanError(obj)
