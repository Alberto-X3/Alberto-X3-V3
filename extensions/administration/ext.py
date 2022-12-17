__all__ = ("Administration",)


from AlbertoX3 import get_logger, Extension
from naff import Client
from .exts import Sudo, Permissions


logger = get_logger(__name__)


class Administration(Sudo, Permissions, baseclass=Extension):
    def __init__(self, bot: Client):
        Sudo.__init__(self, bot)
