__all__ = (
    "AlbertoX3Error",
    "DeveloperError",
    "DeveloperArgumentError",
    "GatherAnyError",
    "UnrecognisedBooleanError",
)


class AlbertoX3Error(Exception):
    """
    Base for every Exception from AlbertoX3.
    """


class DeveloperError(AlbertoX3Error):
    pass


class DeveloperArgumentError(DeveloperError):
    pass


class GatherAnyError(AlbertoX3Error):
    def __init__(self, idx, exception):
        self.idx = idx
        self.exception = exception


class UnrecognisedBooleanError(AlbertoX3Error):
    pass
