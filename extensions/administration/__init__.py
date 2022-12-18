__all__ = (
    "Administration",
    "setup",
)


from .ext import Administration


def setup(bot):
    Administration(bot)
