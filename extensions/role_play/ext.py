__all__ = ("RolePlay",)


from AlbertoX3 import get_logger, Extension
from naff import Client
from .exts import CaseFile


logger = get_logger(__name__)


class RolePlay(CaseFile, baseclass=Extension):
    def __init__(self, bot: Client):
        CaseFile.__init__(self, bot)
