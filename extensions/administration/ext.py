__all__ = ("Administration",)


from AlbertoX3.naff_wrapper import Extension
from AlbertoX3.utils import get_logger
from naff.client.client import Client
from .exts import Sudo, Roles, Permissions


logger = get_logger(__name__)


class Administration(Sudo, Roles, Permissions, baseclass=Extension):
    def __init__(self, bot: Client):
        Sudo.__init__(self, bot)
