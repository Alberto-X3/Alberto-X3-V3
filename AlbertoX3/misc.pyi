from typing import Callable

class FormatStr(str):
    __call__: Callable[..., str]  # see str.format
