__all__ = ("RolePlayPermission",)


from aenum import auto
from AlbertoX3.permission import BasePermission
from AlbertoX3.translations import t


class RolePlayPermission(BasePermission):
    @property
    def description(self) -> str:
        return t.role_play.permissions[self.name]

    cf_view = auto()
    cf_create = auto()
    cf_edit = auto()
    cf_delete = auto()
