from pathlib import Path
from .contributors import Contributor
from .misc import FormatStr

LIB_PATH: Path

class Config:
    _instance: list[Config]

    # bot
    NAME: str
    VERSION: str
    PREFIX: str

    # repo
    REPO_OWNER: str
    REPO_NAME: str
    REPO_LINK: str
    REPO_ICON: str

    # help
    SUPPORT_DISCORD: str

    # developers
    AUTHOR: Contributor
    CONTRIBUTORS: set[Contributor]

    # language
    LANGUAGE_DEFAULT: str
    LANGUAGE_FALLBACK: str
    LANGUAGE_AVAILABLE: list[str]

    # extensions
    EXTENSIONS_FOLDER_RAW: str
    EXTENSIONS_FOLDER: Path
    EXTENSIONS: ...  # set[PrimitiveExtensions]

    # tmp
    TMP_FOLDER_RAW: str
    TMP_FOLDER: Path
    TMP_PATTERN: FormatStr
    TMP_REMOVE_AUTO: bool
    TMP_REMOVE_ON_STARTUP: bool

    def __new__(cls, path: Path) -> Config: ...

class StyleConfig:
    t_attribute: str
    t_value: str
    vl: str
    vm: str
    vr: str
    ht: str
    hm: str
    hb: str
    tl: str
    tm: str
    tr: str
    ml: str
    mm: str
    mr: str
    bl: str
    bm: str
    br: str
    def __new__(
        cls,
        t_attribute: str = ...,
        t_value: str = ...,
        vl: str = ...,
        vm: str = ...,
        vr: str = ...,
        ht: str = ...,
        hm: str = ...,
        hb: str = ...,
        tl: str = ...,
        tm: str = ...,
        tr: str = ...,
        ml: str = ...,
        mm: str = ...,
        mr: str = ...,
        bl: str = ...,
        bm: str = ...,
        br: str = ...,
    ) -> StyleConfig: ...
    @classmethod
    def from_dict(cls, d: dict[str, str], /) -> StyleConfig: ...
