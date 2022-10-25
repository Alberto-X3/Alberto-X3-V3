__all__ = ("Debug",)


from naff import Client
from .ext import Debug


def setup(bot: Client):
    Debug(bot)
