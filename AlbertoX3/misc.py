__all__ = ("FormatStr",)


class FormatStr(str):
    __call__ = str.format
