__all__ = (
    "LIB_PATH",
    "Config",
)


from pathlib import Path
from yaml import safe_load
from .contributors import Contributor


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
        cls.TMP_PATTERN = ...  # FormatStr(config["tmp"]["pattern"])
        cls.TMP_REMOVE_AUTO = ...  # get_bool(config["tmp"]["remove"]["auto"])
        cls.TMP_REMOVE_ON_STARTUP = ...  # get_bool(config["tmp"]["remove"]["on_startup"])

        # getting the instance
        if not cls._instance:
            self = super().__new__(cls)
            cls._instance.append(self)
        else:
            self = cls._instance[0]

        return self
