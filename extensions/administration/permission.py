__all__ = ("AdministrationPermission",)


from aenum import auto
from AlbertoX3 import BasePermission


class AdministrationPermission(BasePermission):
    @property
    def description(self) -> str:
        return "ADD DESCRIPTION TO ADMINISTRATION-PERMISSION!!!"

    s_clear_cache = auto()
    s_reload = auto()
    s_stop = auto()
    s_kill = auto()
