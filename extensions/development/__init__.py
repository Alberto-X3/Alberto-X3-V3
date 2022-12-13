__all__ = (
    "Debug",
    "setup",
)


from .ext import Debug


def setup(bot):
    Debug(bot)
