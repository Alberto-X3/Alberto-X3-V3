__all__ = ("RolePlay",)


from AlbertoX3.naff_wrapper import Extension
from AlbertoX3.utils import get_logger
from naff.client.client import Client
from .exts import CaseFile


logger = get_logger(__name__)


class RolePlay(CaseFile, baseclass=Extension):
    def __init__(self, bot: Client):
        CaseFile.__init__(self, bot)
