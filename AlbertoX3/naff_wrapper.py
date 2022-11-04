__all__ = ("Extension",)


from naff import (
    Extension as naff_Extension,
    BaseCommand as naff_BaseCommand,
    Listener as naff_Listener,
    Task as naff_Task,
)
from typing import NoReturn, Any
from .database import db_wrapper


class Extension(naff_Extension):
    def __init_subclass__(cls, add_database_wrapper: bool = True, **kwargs: Any) -> NoReturn:
        if add_database_wrapper is True:
            for attr in dir(cls):
                val = getattr(cls, attr)
                if isinstance(val, naff_BaseCommand):
                    if val.checks:
                        val.checks = [db_wrapper(check) for check in val.checks]
                    if val.error_callback:
                        val.error_callback = db_wrapper(val.error_callback)
                    if val.pre_run_callback:
                        val.pre_run_callback = db_wrapper(val.pre_run_callback)
                    if val.post_run_callback:
                        val.post_run_callback = db_wrapper(val.post_run_callback)
                if isinstance(val, (naff_BaseCommand, naff_Listener, naff_Task)):
                    if val.callback:
                        val.callback = db_wrapper(val.callback)
