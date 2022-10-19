from naff import Missing, Absent
from pathlib import Path
from .contributors import Contributor
from .misc import FormatStr, PrimitiveExtension

LIB_PATH: Path
MISSING: Missing

class Config:
    _instance: list[Config]  # length: max 1

    # bot
    NAME: Absent[str]
    VERSION: Absent[str]
    PREFIX: Absent[str]

    # repo
    REPO_OWNER: Absent[str]
    REPO_NAME: Absent[str]
    REPO_LINK: Absent[str]
    REPO_ICON: Absent[str]

    # help
    SUPPORT_DISCORD: Absent[str]

    # developers
    AUTHOR: Absent[Contributor]
    CONTRIBUTORS: Absent[set[Contributor]]

    # language
    LANGUAGE_DEFAULT: Absent[str]
    LANGUAGE_FALLBACK: Absent[str]
    LANGUAGE_AVAILABLE: Absent[list[str]]

    # extensions
    EXTENSIONS_FOLDER_RAW: Absent[str]
    EXTENSIONS_FOLDER: Absent[Path]
    EXTENSIONS: Absent[set[PrimitiveExtension]]

    # tmp
    TMP_FOLDER_RAW: Absent[str]
    TMP_FOLDER: Absent[Path]
    TMP_PATTERN: Absent[FormatStr]
    TMP_REMOVE_AUTO: Absent[bool]
    TMP_REMOVE_ON_STARTUP: Absent[bool]

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
        t_attribute: Absent[str] = ...,
        t_value: Absent[str] = ...,
        vl: Absent[str] = ...,
        vm: Absent[str] = ...,
        vr: Absent[str] = ...,
        ht: Absent[str] = ...,
        hm: Absent[str] = ...,
        hb: Absent[str] = ...,
        tl: Absent[str] = ...,
        tm: Absent[str] = ...,
        tr: Absent[str] = ...,
        ml: Absent[str] = ...,
        mm: Absent[str] = ...,
        mr: Absent[str] = ...,
        bl: Absent[str] = ...,
        bm: Absent[str] = ...,
        br: Absent[str] = ...,
    ) -> StyleConfig: ...
    @classmethod
    def from_dict(cls, d: dict[str, str], /) -> StyleConfig: ...
