__all__ = (
    "Automation",
    "setup",
)


from .ext import Automation


def setup(bot):
    Automation(bot)
