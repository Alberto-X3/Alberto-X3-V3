__all__ = (
    "LIB_PATH",
    "MISSING",
    "Config",
    "StyleConfig",
)


from naff import Missing, Absent
from pathlib import Path
from yaml import safe_load
from .contributors import Contributor
from .misc import FormatStr, PrimitiveExtension


LIB_PATH: Path = Path().resolve()
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

    def __new__(cls, path: Path):
        # due to circular imports
        from .utils import get_bool, get_lib_version

        config = safe_load(path.read_text("utf-8"))

        # bot
        cls.NAME = config["name"]
        cls.VERSION = get_lib_version()
        cls.PREFIX = config["prefix"]

        # repo
        cls.REPO_OWNER = config["repo"]["owner"]
        cls.REPO_NAME = config["repo"]["name"]
        cls.REPO_LINK = f"https://github.com/{cls.REPO_OWNER}/{cls.REPO_NAME}"
        cls.REPO_ICON = config["repo"]["icon"]

        # help
        cls.SUPPORT_DISCORD = config["discord"]

        # developers
        cls.AUTHOR = Contributor.AlbertUnruh
        cls.CONTRIBUTORS = set(Contributor.__members__.values())

        # language
        cls.LANGUAGE_DEFAULT = config["language"]["default"]
        cls.LANGUAGE_FALLBACK = config["language"]["fallback"]
        cls.LANGUAGE_AVAILABLE = config["language"]["available"]

        # extensions
        cls.EXTENSIONS_FOLDER_RAW = (folder := config["extensions"]["folder"])
        folder = Path(folder)
        if not folder.is_absolute():
            folder = LIB_PATH.joinpath(folder)
        cls.EXTENSIONS_FOLDER = folder
        cls.EXTENSIONS = MISSING

        # tmp
        cls.TMP_FOLDER_RAW = (folder := config["tmp"]["folder"])
        folder = Path(folder)
        if not folder.is_absolute():
            folder = LIB_PATH.joinpath(folder)
        cls.TMP_FOLDER = folder
        cls.TMP_PATTERN = FormatStr(config["tmp"]["pattern"])
        cls.TMP_REMOVE_AUTO = get_bool(config["tmp"]["remove"]["auto"])
        cls.TMP_REMOVE_ON_STARTUP = get_bool(config["tmp"]["remove"]["on_startup"])

        # getting the instance
        if not cls._instance:
            self = super().__new__(cls)
            cls._instance.append(self)
        else:
            self = cls._instance[0]

        return self


class StyleConfig:
    """
    Used in over in .utils for get_value_table().
    """

    __slots__ = ()

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
