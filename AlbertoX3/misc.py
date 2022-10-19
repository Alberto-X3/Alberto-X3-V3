__all__ = (
    "FormatStr",
    "PrimitiveExtension",
)


class FormatStr(str):
    __call__ = str.format


class PrimitiveExtension:
    def __init__(self, name, package, path):
        self.name = name
        self.package = package
        self.path = path

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.name!r} at {self.path})>"

    def __str__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"
