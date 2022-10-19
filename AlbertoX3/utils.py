__all__ = (
    "get_value_table",
    "get_bool",
    "get_lib_version",
    "get_subclasses_in_extensions",
    "get_language",
    "get_member",
    "get_user",
)


import re
from naff import User, Member, MISSING
from .errors import DeveloperArgumentError

# Note: using naff.MISSING to avoid circular imports from .constants


def get_value_table(obj, /, *, style=MISSING):
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

    if style is MISSING:
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
    raise ValueError


_VERSION_REGEX = re.compile(r"^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]", re.MULTILINE)


def get_lib_version():
    # circular imports...
    from .contants import LIB_PATH

    file = LIB_PATH.joinpath("__init__.py").read_text("utf-8")
    if (result := _VERSION_REGEX.search(file)) is None:
        version = "0.0.0"
    else:
        version = result.group(1)

    try:
        import subprocess  # noqa S404

        # commit count
        p = subprocess.Popen(  # noqa S603, S607
            ["git", "rev-list", "--count", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()  # type: bytes, bytes
        if out:
            version += f"+{out.decode('utf-8').strip()}"

        # commit sha
        p = subprocess.Popen(  # noqa S603, S607
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()  # type: bytes, bytes
        if out:
            version += f"+g{out.decode('utf-8').strip()}"

    except Exception as e:  # noqa  # ToDo: logging
        ...

    return version


def get_subclasses_in_extensions(base, *, extensions=MISSING):  # noqa
    # isn't implemented yet -> is static
    return []


def get_language(*, guild=MISSING, user=MISSING):
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

    Raises
    ------
    DeveloperArgumentError
        If either both (``guild`` and ``user``) or none of them are set.
    """
    # both are set
    if guild is not MISSING and user is not MISSING:
        raise DeveloperArgumentError("Can't set both ('guild' and 'user')!")
    # neither are set
    if guild is MISSING and user is MISSING:
        raise DeveloperArgumentError("Either 'guild' or 'user' have to be set!")

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
                for (_g_id, _u_id), member in ctx.bot.cache.member_cache.items():  # type: (int, int), Member
                    if _g_id != ctx.guild_id:
                        continue
                    if member.username == name and member.discriminator == discriminator:
                        return member

            # name?
            for (_g_id, _u_id), member in ctx.bot.cache.member_cache.items():  # type: (int, int), Member
                if _g_id != ctx.guild_id:
                    continue
                if member.username == raw:
                    return member

            # nick?
            for (_g_id, _u_id), member in ctx.bot.cache.member_cache.items():  # type: (int, int), Member
                if _g_id != ctx.guild_id:
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
