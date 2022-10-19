__all__ = (
    "LIB_PATH",
    "Config",
    "StyleConfig",
)


from pathlib import Path
from yaml import safe_load
from .contributors import Contributor
from .misc import FormatStr
from .utils import get_bool


LIB_PATH = Path(__file__).parent


class Config:
    """
    Global configuration for the bot.
    """

    _instance = []

    def __new__(cls, path):
        config = safe_load(path.read_text("utf-8"))

        # bot
        cls.NAME = config["name"]
        cls.VERSION = ...
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
        cls.EXTENSIONS = ...

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

    t_attribute = "Attribute"
    t_value = "Value"
    vl = "║"  # vertical left
    vm = "│"  # vertical middle
    vr = "║"  # vertical right
    ht = "═"  # horizontal top
    hm = "═"  # horizontal middle
    hb = "═"  # horizontal bottom
    tl = "╔"  # top left
    tm = "╤"  # top middle (connector)
    tr = "╗"  # top right
    ml = "╠"  # middle left (connector)
    mm = "╪"  # center
    mr = "╣"  # middle right (connector)
    bl = "╚"  # bottom left
    bm = "╧"  # bottom middle (connector)
    br = "╝"  # bottom right

    def __new__(
        cls,
        t_attribute=None,
        t_value=None,
        vl=None,
        vm=None,
        vr=None,
        ht=None,
        hm=None,
        hb=None,
        tl=None,
        tm=None,
        tr=None,
        ml=None,
        mm=None,
        mr=None,
        bl=None,
        bm=None,
        br=None,
    ):
        settings = locals()
        settings.pop("cls")
        return cls.from_dict(settings)

    @classmethod
    def from_dict(cls, d, /):
        self = super().__new__(cls)

        for setting, character in d.items():
            if setting not in dir(self):
                # will be changed to BadConfigArgument when I'm reaching the error-files
                raise ValueError  # invalid setting
            if character is None:  # default from __new__
                continue
            if not isinstance(character, str):
                # will be changed to BadConfigArgument when I'm reaching the error-files
                raise ValueError  # invalid character length

            setattr(self, setting, character)

        return self
