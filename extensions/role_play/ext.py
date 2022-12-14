__all__ = ("RolePlay",)


from AlbertoX3 import get_logger, Extension
from .case_file import CaseFile


logger = get_logger(__name__)


class RolePlay(CaseFile, baseclass=Extension):
    ...
