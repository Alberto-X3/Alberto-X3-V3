__all__ = ("RolePlayPermission",)


from aenum import auto
from AlbertoX3 import BasePermission


class RolePlayPermission(BasePermission):
    @property
    def description(self) -> str:
        return "ADD DESCRIPTION TO RP-PERMISSION!!!"

    cf_view = auto()
    cf_create = auto()
    cf_edit = auto()
    cf_delete = auto()
