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

    r_config_read = auto()
    r_config_write = auto()
    r_list_members = auto()
    r_roles_clone = auto()
