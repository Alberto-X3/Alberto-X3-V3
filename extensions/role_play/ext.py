__all__ = ("RolePlay",)


from AlbertoX3 import get_logger, Extension
from .file_case import FileCase


logger = get_logger(__name__)


class RolePlay(FileCase, baseclass=Extension):
    ...
