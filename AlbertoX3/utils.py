__all__ = (
    "get_value_table",
    "get_bool",
    "get_subclasses_in_extensions",
    "get_language",
    "get_member",
    "get_user",
)


import re
from naff import User, Member


def get_value_table(obj, /, *, style=None):
    """
    Creates a nice table with attributes and their values.

    Parameters
    ----------
    obj: object
        The object to get the values from.
    style: dict[str, str], StyleConfig
        The style to use. Defaults to StyleConfig.

    Returns
    -------
    str
        The value-table as a str.

    Examples
    --------
    >>> from AlbertoX3.utils import get_value_table
    >>> class Foo:
    ...     FOO = True
    ...     def __init__(self):
    ...         self.bar = "chocolate?"
    ...         self.spam = "EGG!!1!"
    >>> print(get_value_table(Foo))  # without __init__
    ... # ╔═══════════╤═══════╗
    ... # ║ Attribute │ Value ║
    ... # ╠═══════════╪═══════╣
    ... # ║ FOO       │ True  ║
    ... # ╚═══════════╧═══════╝
    >>> print(get_value_table(Foo()))  # with __init__
    ... # ╔═══════════╤══════════════╗
    ... # ║ Attribute │ Value        ║
    ... # ╠═══════════╪══════════════╣
    ... # ║ FOO       │ True         ║
    ... # ║ bar       │ 'chocolate?' ║
    ... # ║ spam      │ 'EGG!!1!'    ║
    ... # ╚═══════════╧══════════════╝
    """
    # circular imports...
    from .contants import StyleConfig

    if style is None:
        style = StyleConfig()
    if isinstance(style, dict):
        style = StyleConfig.from_dict(style)

    arguments = [a for a in dir(obj) if not a.startswith("_")]
    values = [f"{getattr(obj, a)!r}" for a in arguments]

    len_a = len(max(arguments + [style.t_attribute], key=len))
    len_v = len(max(values + [style.t_value], key=len))

    lines: list[str] = [
        f"{style.tl}{(len_a + 2) * style.ht}{style.tm}{(len_v + 2) * style.ht}{style.tr}",
        f"{style.vl} {style.t_attribute.ljust(len_a)} {style.vm} {style.t_value.ljust(len_v)} {style.vr}",
        f"{style.ml}{(len_a + 2) * style.hm}{style.mm}{(len_v + 2) * style.hm}{style.mr}",
    ]

    for a, v in zip(arguments, values):
        lines.append(
            f"{style.vl} {a.ljust(len_a)} {style.vm} {v.ljust(len_v)} {style.vr}",
        )

    lines.append(
        f"{style.bl}{(len_a + 2) * style.hb}{style.bm}{(len_v + 2) * style.hb}{style.br}",
    )

    return "\n".join(lines)


def get_bool(obj, /):
    """
    Currently matches:
        - True -> boolean, 1, lowered("true", "t", "yes", "y"), "1"
        - False -> boolean, -1, 0, lowered("false", "f", "no", "n"), "-1", "0"

    Parameters
    ----------
    obj: object
        The object to match (should be bool, int or str; others aren't supported at the moment)

    Returns
    -------
    bool
        The matched boolean.

    Raises
    ------
    UnrecognisedBooleanError
        Raised when the object couldn't be matched to a boolean.
    """
    match obj:
        case bool():
            return obj
        case int():
            match obj:
                case 1:
                    return True
                case -1 | 0:
                    return False
        case str():
            match obj.lower():  # type: ignore
                case "true" | "t" | "yes" | "y" | "1":
                    return True
                case "false" | "f" | "no" | "n" | "-1" | "0":
                    return False
    # will be changed to UnrecognisedBooleanError when I'm reaching the error-files
    raise ValueError()


def get_subclasses_in_extensions(base, *, extensions=None):  # noqa
    # isn't implemented yet -> is static
    return []


def get_language(*, guild=None, user=None):
    """
    Gets a set language by a guild or a user.

    **This function isn't completely implemented and returns ``None``.**
    **Besides that it already validates the given arguments.**

    Notes
    -----
    Only *one* argument can be set. Either ``guild`` *or* ``user``!

    Parameters
    ----------
    guild: Guild, SnowflakeType
        The guild to get the set language.
    user: User, Member, SnowflakeType
        The user to get the set language.

    Returns
    -------
    str, optional
        Returns the set language if one is set, otherwise None.
    """
    # both are set
    if guild is not None and user is not None:
        # will be changed to DeveloperArgumentError when I'm reaching the error-files
        raise ValueError()  # can't set both
    # neither are set
    if guild is None and user is None:
        # will be changed to DeveloperArgumentError when I'm reaching the error-files
        raise ValueError()  # must set one

    # ToDo: connect to database
    # Note (for future me): you should call an async function in here for the database ;)
    return None


_ID_REGEX = re.compile(r"^(\d{7,20})$")
_MENTION_REGEX = re.compile(r"^<@!?(\d{7,20})>$")
_NAME_REGEX = re.compile(r"^(.{2,32})#(\d{4})$")


async def get_member(ctx, raw):
    """
    Get a member from the context's guild.

    Parameters
    ----------
    ctx: Context
    raw: Member, User, SnowflakeType
        The member to find.

    Returns
    -------
    Member, optional
        The found member.
    """
    match raw:
        case Member():
            return raw

        case User():
            return await ctx.bot.fetch_member(ctx.guild_id, raw.id)

        case _ if _ID_REGEX.match(str(raw)) is not None:  # also covers int() via regex
            return await ctx.bot.fetch_member(ctx.guild_id, int(raw))

        case int():
            # only invalid id's get here
            return None

        case str():
            # mention?
            if (result := _MENTION_REGEX.match(raw)) is not None:
                return await ctx.bot.fetch_member(ctx.guild_id, result.group(1))

            # name#discriminator?
            if (result := _NAME_REGEX.match(raw)) is not None:
                name, discriminator = result.groups()
                # cold also be done via ctx.guild.members, but get_user() would need this way anyway
                for (g_id, u_id), member in ctx.bot.cache.member_cache.items():  # type: (int, int), Member
                    if g_id != ctx.guild_id:
                        continue
                    if member.username == name and member.discriminator == discriminator:
                        return member

            # name?
            for (g_id, u_id), member in ctx.bot.cache.member_cache.items():  # type: (int, int), Member
                if g_id != ctx.guild_id:
                    continue
                if member.username == raw:
                    return member

            # nick?
            for (g_id, u_id), member in ctx.bot.cache.member_cache.items():  # type: (int, int), Member
                if g_id != ctx.guild_id:
                    continue
                if member.nickname == raw:
                    return member

            # are name/nick lowercase?
            if not raw.islower():
                return await get_member(ctx, raw.lower())
            else:
                # get_user() already called itself with lowercase-name
                return None

        case _ if hasattr(raw, "__int__"):
            # maybe a SnowflakeObject was passed
            return await get_member(ctx, int(raw))

        case _:
            return None


async def get_user(ctx, raw):
    """
    Parameters
    ----------
    ctx: Context
    raw: User, Member, SnowflakeType
        The user to search for.

    Returns
    -------
    User, optional
        The found user.
    """
    match raw:
        case User():
            return raw

        case Member():
            return raw.user

        case _ if _ID_REGEX.match(str(raw)) is not None:  # also covers int() via regex
            return await ctx.bot.fetch_user(int(raw))

        case int():
            # only invalid id's get here
            return None

        case str():
            # mention?
            if (result := _MENTION_REGEX.match(raw)) is not None:
                return await ctx.bot.fetch_user(result.group(1))

            # name#discriminator?
            if (result := _NAME_REGEX.match(raw)) is not None:
                name, discriminator = result.groups()
                for user in ctx.bot.cache.user_cache.items():  # type: User
                    if user.username == name and user.discriminator == discriminator:
                        return user

            # name?
            for user in ctx.bot.cache.user_cache.items():  # type: User
                if user.username == raw:
                    return user

            # is name lowercase?
            if not raw.islower():
                return await get_member(ctx, raw.lower())
            else:
                # get_user() already called itself with lowercase-name
                return None

        case _ if hasattr(raw, "__int__"):
            # maybe a SnowflakeObject was passed
            return await get_member(ctx, int(raw))

        case _:
            return None