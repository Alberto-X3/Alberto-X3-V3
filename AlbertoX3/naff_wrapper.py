__all__ = ("Extension",)


from naff import (
    Extension as naff_Extension,
    BaseCommand as naff_BaseCommand,
    Listener as naff_Listener,
    Task as naff_Task,
)
from typing import NoReturn, Any, TypeVar, ParamSpec, Callable, Awaitable
from .database import db_wrapper
from .translations import language_wrapper


T = TypeVar("T")
P = ParamSpec("P")


def multi_wrap(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    if getattr(func, "_is_multi_wrapped_by_naff_wrapper", False) is False:
        func = db_wrapper(language_wrapper(func))
        func._is_multi_wrapped_by_naff_wrapper = True
    return func


class Extension(naff_Extension):
    def __init_subclass__(cls, **kwargs: Any) -> NoReturn:
        for attr in dir(cls):
            val = getattr(cls, attr)
            if isinstance(val, naff_BaseCommand):
                if val.checks:
                    val.checks = [multi_wrap(check) for check in val.checks]
                if val.error_callback:
                    val.error_callback = multi_wrap(val.error_callback)
                if val.pre_run_callback:
                    val.pre_run_callback = multi_wrap(val.pre_run_callback)
                if val.post_run_callback:
                    val.post_run_callback = multi_wrap(val.post_run_callback)
            if isinstance(val, (naff_BaseCommand, naff_Listener, naff_Task)):
                if val.callback:
                    val.callback = multi_wrap(val.callback)
