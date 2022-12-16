__all__ = (
    "language",
    "Translations",
    "TranslationNamespace",
    "merge",
    "load_translations",
    "t",
)


from contextvars import ContextVar
from naff import Absent
from pathlib import Path
from typing import NoReturn
from yaml import safe_load
from .constants import Config, MISSING
from .errors import UnsupportedLanguageError, UnsupportedTranslationTypeError
from .misc import FormatStr, PrimitiveExtension
from .utils import get_logger


logger = get_logger(__name__)

language: ContextVar[str] = ContextVar("language")


def merge(base: dict, src: dict) -> dict:
    """
    Merges to dictionaries recursively.

    Parameters
    ----------
    base: dict
        The dictionary to merge into.
    src: dict
        The dictionary to merge into ``base``.

    Returns
    -------
    dict
        The merged dictionary.
    """
    for k, v in src.items():
        if k in base and isinstance(v, dict) and isinstance(base[k], dict):
            merge(base[k], v)
        else:
            base[k] = v

    return base


class TranslationDict(dict):
    _fallback: dict

    def __call__(self, *args: object, **kwargs: object) -> str:
        cnt = kwargs.get("cnt", kwargs.get("count", None))

        translation: FormatStr
        if cnt == 1:
            translation = self.one
        elif cnt == 0 and "zero" in self:  # optional
            translation = self.zero
        else:
            translation = self.many

        return translation(*args, **kwargs)

    def __getattr__(self, item: str) -> "TranslationDict | FormatStr":
        value: dict | str = self.get(item, self._fallback[item])
        result: TranslationDict | FormatStr

        if isinstance(value, str):
            result = FormatStr(value)
        elif isinstance(value, dict):
            result = TranslationDict(value)
            result._fallback = self._fallback[item]
        else:
            raise UnsupportedTranslationTypeError(key=item, type=type(value), supported=[dict, str])

        return result

    def __contains__(self, item: object) -> bool:
        return super().__contains__(item) or self._fallback.__contains__(item)


class TranslationNamespace:
    _sources: list[Path]
    _translations: dict[str, dict[str, ...]]

    def __init__(self):
        self._sources = []
        self._translations = {}

    def tn_add_source(self, source: Path) -> NoReturn:
        self._sources.append(source)
        self._translations.clear()

    def tn_get_language(self, lan: str) -> dict[str, ...]:
        if lan not in Config.LANGUAGE_AVAILABLE:
            raise UnsupportedLanguageError(language=lan)

        if lan not in self._translations:
            logger.debug(f"Creating translations for {lan!r}")
            self._translations[lan] = {}
            for source in self._sources:
                if not (path := source / f"{lan}.yml".lower()).exists():
                    continue
                with path.open() as file:
                    merge(self._translations[lan], safe_load(file) or {})

        return self._translations[lan]

    def tn_get_translation(self, key: str, lan: str = MISSING) -> dict | str:
        if lan is MISSING:
            lan = language.get(Config.LANGUAGE_DEFAULT)
        translations = self.tn_get_language(lan)

        if key not in translations:
            translations = self.tn_get_language(Config.LANGUAGE_FALLBACK)

        if not isinstance(translation := translations[key], (dict, str)):
            raise UnsupportedTranslationTypeError(key=key, type=type(translation))

        return translation

    def __getattr__(self, item: str) -> TranslationDict | FormatStr:
        value: dict | str = self.tn_get_translation(item)
        result: TranslationDict | FormatStr

        if isinstance(value, str):
            result = FormatStr(value)
        elif isinstance(value, dict):
            result = TranslationDict(value)
            result._fallback = self.tn_get_language(Config.LANGUAGE_FALLBACK)[item]
        else:
            raise UnsupportedTranslationTypeError(key=item, type=type(value), supported=[dict, str])

        return result


class Translations:
    # do I need this line below? may be removed in future versions
    # FALLBACK: str = Config.LANGUAGE_FALLBACK
    _namespace: dict[str, TranslationNamespace]

    def __init__(self):
        self._namespace = {}

    def register_translation_namespace(self, name: str, file: Path) -> NoReturn:
        if name not in self._namespace:
            logger.debug(f"Creating TranslationNamespace for {name!r}")
            self._namespace[name] = TranslationNamespace()
        else:
            logger.debug(f"Extending TranslationNamespace for {name!r}")

        self._namespace[name].tn_add_source(file)

    def __getattr__(self, item: str) -> TranslationNamespace:
        return self._namespace[item]


def load_translations(
    *,
    translations: Absent[Translations] = MISSING,
    extensions: Absent[list[PrimitiveExtension]] = MISSING,
    translation_folder: str = "translations",
) -> NoReturn:
    """
    Loads translations from the extensions.

    Parameters
    ----------
    translations: Translations
        The translations to load into (defaults to ``translations.t``)
    extensions: list[PrimitiveExtension]
        The scales to look at (defaults to ``Config.EXTENSIONS``).
    translation_folder: str
        The name of the translation folder.
    """
    if translations is MISSING:
        translations = t

    if extensions is MISSING:
        extensions = Config.EXTENSIONS

    for ext in extensions:
        if (path := ext.path.joinpath(translation_folder)).is_dir():
            for lan in Config.LANGUAGE_AVAILABLE:
                if (path.joinpath(f"{lan}.yml".lower())).is_file():
                    translations.register_translation_namespace(path.parent.name, path)


# global translations container
t: Translations = Translations()

# global translations namespace
t.register_translation_namespace("g", Path(__file__).parent / "translations")
