__all__ = (
    "LIB_PATH",
    "MISSING",
    "Config",
    "StyleConfig",
)


from functools import partial
from naff import Member, Missing, Absent, User
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Awaitable, NoReturn
from yaml import safe_load
from .contributors import Contributor
from .errors import InvalidPermissionLevelError
from .misc import FormatStr, PrimitiveExtension

if TYPE_CHECKING:
    # needed for type hinting and to avoid circular imports
    from .permission import BasePermissionLevel, PermissionLevel


LIB_PATH: Path = Path(__file__).parent
MISSING: Missing = Missing()


class Config:
    """
    Global configuration for the bot.
    """

    __slots__ = ()
    _instance: list["Config"] = []

    # bot
    NAME: Absent[str] = MISSING
    VERSION: Absent[str] = MISSING
    PREFIX: Absent[str] = MISSING
    # repo
    REPO_OWNER: Absent[str] = MISSING
    REPO_NAME: Absent[str] = MISSING
    REPO_LINK: Absent[str] = MISSING
    REPO_ICON: Absent[str] = MISSING
    # help
    SUPPORT_DISCORD: Absent[str] = MISSING
    # developers
    AUTHOR: Absent[Contributor] = MISSING
    CONTRIBUTORS: Absent[set[Contributor]] = MISSING
    # language
    LANGUAGE_DEFAULT: Absent[str] = MISSING
    LANGUAGE_FALLBACK: Absent[str] = MISSING
    LANGUAGE_AVAILABLE: Absent[list[str]] = MISSING
    # extensions
    EXTENSIONS_FOLDER_RAW: Absent[str] = MISSING
    EXTENSIONS_FOLDER: Absent[Path] = MISSING
    EXTENSIONS: Absent[set[PrimitiveExtension]] = MISSING
    # tmp
    TMP_FOLDER_RAW: Absent[str] = MISSING
    TMP_FOLDER: Absent[Path] = MISSING
    TMP_PATTERN: Absent[FormatStr] = MISSING
    TMP_REMOVE_AUTO: Absent[bool] = MISSING
    TMP_REMOVE_ON_STARTUP: Absent[bool] = MISSING
    # auto
    AUTO_HOUR: Absent[int] = MISSING
    AUTO_MINUTE: Absent[int] = MISSING
    AUTO_SECOND: Absent[int] = MISSING
    AUTO_CHANNEL: Absent[int] = MISSING
    # permission
    PERMISSION_DEFAULT_OVERRIDES: Absent[dict[str, dict[str, "BasePermissionLevel"]]] = MISSING
    PERMISSION_DEFAULT_LEVEL: Absent[str] = MISSING
    PERMISSION_LEVELS: Absent[type["BasePermissionLevel"]] = MISSING
    PERMISSION_LEVEL_TEAM: Absent["PermissionLevel"] = MISSING

    def __new__(cls, path: Path):
        # due to circular imports
        from .utils import get_bool, get_lib_version, get_extensions

        config: dict[str, ...] = safe_load(path.read_text("utf-8"))

        # bot
        cls.NAME = config.get("name", MISSING)
        cls.VERSION = get_lib_version()
        cls.PREFIX = config["prefix"]

        # repo
        repo: Absent[dict[str, str]] = config.get("repo", MISSING)
        if repo is not MISSING:
            cls.REPO_OWNER = repo["owner"]
            cls.REPO_NAME = repo["name"]
            cls.REPO_LINK = f"https://github.com/{cls.REPO_OWNER}/{cls.REPO_NAME}"
            cls.REPO_ICON = repo["icon"]

        # help
        cls.SUPPORT_DISCORD = config.get("discord", MISSING)

        # developers
        cls.AUTHOR = Contributor.AlbertUnruh
        cls.CONTRIBUTORS = set(Contributor.__members__.values())

        # language
        language: dict[str, str | list[str]] = config.get("language", {})
        cls.LANGUAGE_DEFAULT = language.get("default", "EN")
        cls.LANGUAGE_FALLBACK = language.get("fallback", cls.LANGUAGE_FALLBACK)
        cls.LANGUAGE_AVAILABLE = language.get("available", [cls.LANGUAGE_FALLBACK])

        # extensions
        extensions: dict[str, str] = config.get("extensions", {})
        cls.EXTENSIONS_FOLDER_RAW = (folder := extensions.get("folder", "extensions"))
        folder = Path(folder)
        if not folder.is_absolute():
            folder = path.parent.joinpath(folder)
        cls.EXTENSIONS_FOLDER = folder
        cls.EXTENSIONS = get_extensions()

        # tmp
        tmp: dict[str, str | dict[str, str]] = config.get("tmp", {})
        cls.TMP_FOLDER_RAW = (folder := tmp.get("folder", "tmp"))
        folder = Path(folder)
        if not folder.is_absolute():
            folder = path.parent.joinpath(folder)
        cls.TMP_FOLDER = folder
        cls.TMP_PATTERN = FormatStr(tmp.get("pattern", "{extension}.{id}.alberto-x3.tmp"))
        cls.TMP_REMOVE_AUTO = get_bool(tmp.get("remove", {}).get("auto", True))
        cls.TMP_REMOVE_ON_STARTUP = get_bool(tmp.get("remove", {}).get("on_startup", True))

        # auto
        cls.AUTO_HOUR = 0
        cls.AUTO_MINUTE = 0
        cls.AUTO_SECOND = 0
        cls.AUTO_CHANNEL = 822589081337724939

        # permission
        cls.PERMISSION_DEFAULT_OVERRIDES = {}  # will be further modified in next line
        cls.__load_permission(
            permission_levels_raw=config.get("permission_levels", {}),
            permission_level_team_raw=config.get("team_permission_level", "public"),
            permission_level_default_raw=config.get("default_permission_level", "owner"),
            permission_default_overrides_raw=config.get("default_permission_overrides", {}),
        )  # a bit more logic is needed to load the config

        # getting the instance
        if not cls._instance:
            self = super().__new__(cls)
            cls._instance.append(self)
        else:
            self = cls._instance[0]

        return self

    @classmethod
    def __load_permission(
        cls,
        permission_levels_raw: dict,
        permission_level_team_raw: str,
        permission_level_default_raw: str,
        permission_default_overrides_raw: dict[str, dict[str, str]],
    ) -> NoReturn:
        from .permission import BasePermissionLevel, PermissionLevel
        from .settings import RoleSettings

        permission_levels: dict[str, PermissionLevel] = {
            "public": PermissionLevel(0, ["public", "p"], "Public", [], [])
        }

        for k, v in permission_levels_raw.items():
            if (level := v["level"]) <= 0:
                raise InvalidPermissionLevelError(level=level)

            permission_levels[k] = PermissionLevel(
                level=level,
                aliases=v["aliases"],
                description=v["name"],
                guild_permissions=v["if"].get("permissions", []),
                roles=v["if"].get("roles", []),
            )

        owner_level = max(([pl.level for pl in permission_levels.values()]), default=0) + 1
        permission_levels["owner"] = PermissionLevel(
            level=owner_level, aliases=["owner"], description="Owner", guild_permissions=[], roles=[]
        )

        permission_levels = {
            k.upper(): v for k, v in sorted(permission_levels.items(), key=lambda pl: pl[1].level, reverse=True)
        }
        cls.PERMISSION_LEVELS = BasePermissionLevel("PermissionLevel", permission_levels)
        cls.PERMISSION_LEVELS._get_permission_level = classmethod(
            partial(_get_permission_level, permission_levels, RoleSettings.get)
        )

        cls.PERMISSION_LEVEL_TEAM = getattr(cls.PERMISSION_LEVELS, permission_level_team_raw.upper())
        cls.PERMISSION_DEFAULT_LEVEL = getattr(cls.PERMISSION_LEVELS, permission_level_default_raw.upper())

        for ext, overrides in permission_default_overrides_raw.items():
            for permission, level in overrides.items():
                cls.PERMISSION_DEFAULT_OVERRIDES.setdefault(ext.lower(), {}).setdefault(
                    permission.lower(), getattr(cls.PERMISSION_LEVELS, level.upper())
                )


async def _get_permission_level(
    permission_levels: dict[str, "PermissionLevel"],
    get_role_setting: Callable[[str], Awaitable[int]],  # is AlbertoX3.settings.RoleSettings.get
    cls: "BasePermissionLevel",
    member: User | Member,
) -> "BasePermissionLevel":
    if isinstance(member, User):
        return cls.PUBLIC

    roles = {role.id for role in member.roles}

    async def has_role(role_name: str) -> bool:
        return await get_role_setting(role_name) in roles

    for k, v in permission_levels.items():
        if any(getattr(member.guild_permissions, p.upper()) for p in v.guild_permissions):
            return getattr(cls, k.upper())

        for r in v.roles:
            if await has_role(r):
                return getattr(cls, k.upper())

    return cls.PUBLIC


class StyleConfig:
    """
    Used in over in .utils for get_value_table().
    """

    t_attribute: str = "Attribute"
    t_value: str = "Value"
    vl: str = "║"  # vertical left
    vm: str = "│"  # vertical middle
    vr: str = "║"  # vertical right
    ht: str = "═"  # horizontal top
    hm: str = "═"  # horizontal middle
    hb: str = "═"  # horizontal bottom
    tl: str = "╔"  # top left
    tm: str = "╤"  # top middle (connector)
    tr: str = "╗"  # top right
    ml: str = "╠"  # middle left (connector)
    mm: str = "╪"  # center
    mr: str = "╣"  # middle right (connector)
    bl: str = "╚"  # bottom left
    bm: str = "╧"  # bottom middle (connector)
    br: str = "╝"  # bottom right

    def __new__(
        cls,
        t_attribute: Absent[str] = MISSING,
        t_value: Absent[str] = MISSING,
        vl: Absent[str] = MISSING,
        vm: Absent[str] = MISSING,
        vr: Absent[str] = MISSING,
        ht: Absent[str] = MISSING,
        hm: Absent[str] = MISSING,
        hb: Absent[str] = MISSING,
        tl: Absent[str] = MISSING,
        tm: Absent[str] = MISSING,
        tr: Absent[str] = MISSING,
        ml: Absent[str] = MISSING,
        mm: Absent[str] = MISSING,
        mr: Absent[str] = MISSING,
        bl: Absent[str] = MISSING,
        bm: Absent[str] = MISSING,
        br: Absent[str] = MISSING,
    ):
        settings = locals()
        settings.pop("cls")
        return cls.from_dict(settings)

    @classmethod
    def from_dict(cls, d: dict[str, Absent[str]], /) -> "StyleConfig":
        self = super().__new__(cls)

        for setting, character in d.items():
            if setting not in dir(self):
                # will be changed to BadConfigArgument when I'm reaching the error-files
                raise ValueError  # invalid setting
            if character is MISSING:  # default from __new__
                continue
            if not isinstance(character, str):
                # will be changed to BadConfigArgument when I'm reaching the error-files
                raise ValueError  # invalid character length

            setattr(self, setting, character)

        return self
