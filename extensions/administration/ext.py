__all__ = ("Administration",)


from AlbertoX3 import get_logger, Extension
from naff import Client
from .sudo import Sudo


logger = get_logger(__name__)


class Administration(Sudo, baseclass=Extension):
    def __init__(self, bot: Client):
        Sudo.__init__(self, bot)
