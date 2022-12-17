__all__ = ("AdministrationPermission",)


from aenum import auto
from AlbertoX3 import BasePermission, t


class AdministrationPermission(BasePermission):
    @property
    def description(self) -> str:
        return t.administration.permissions[self.name]

    s_clear_cache = auto()
    s_reload = auto()
    s_stop = auto()
    s_kill = auto()

    p_view_own = auto()
    p_view_all = auto()
    p_manage = auto()
