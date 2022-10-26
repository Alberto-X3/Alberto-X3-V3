__all__ = (
    "Moderation",
    "setup",
)


from .ext import Moderation


def setup(bot):
    Moderation(bot)
