__all__ = ("MaintenancePermission",)


from aenum import auto
from AlbertoX3.permission import BasePermission
from AlbertoX3.translations import t


class MaintenancePermission(BasePermission):
    @property
    def description(self) -> str:
        return t.maintenance.permissions[self.name]

    manage = auto()
