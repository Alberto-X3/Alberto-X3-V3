__all__ = ("RolePlay",)


from AlbertoX3 import get_logger, Extension
from naff import Client
from .case_file import CaseFile


logger = get_logger(__name__)


class RolePlay(CaseFile, baseclass=Extension):
    def __init__(self, bot: Client):
        super().__init__(bot)
