__all__ = (
    "RolePlay",
    "setup",
)


from .ext import RolePlay


def setup(bot):
    RolePlay(bot)
