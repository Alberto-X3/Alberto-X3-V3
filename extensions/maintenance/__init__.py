__all__ = (
    "Maintenance",
    "setup",
)


from .ext import Maintenance


def setup(bot):
    Maintenance(bot)
