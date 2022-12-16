__all__ = ("Sudo",)


from AlbertoX3 import get_logger, Extension, t, TranslationNamespace
from naff import (
    Client,
    BaseChannel,
    BaseCommand,
)


logger = get_logger(__name__)
tg: TranslationNamespace = t.g
t: TranslationNamespace = t.administration.sudo  # real type: TranslationDict


class Sudo(Extension):
    def __init__(self, bot: Client):
        self.s_command_cache: dict[BaseChannel, BaseCommand] = {}
