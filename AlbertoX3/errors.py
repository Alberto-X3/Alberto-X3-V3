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
    idx: int
    exception: Exception

    def __init__(self, idx: int, exception: Exception):
        self.idx = idx
        self.exception = exception

    def __str__(self) -> str:
        # it may be changed in the future as I'll detect more edge-cases
        return f"An error occurred in coroutine {self.idx} while gathering: {self.exception}"


class UnrecognisedBooleanError(AlbertoX3Error):
    obj: object

    def __init__(self, obj: object):
        self.obj = obj

    def __str__(self) -> str:
        return f"Unable to assign {self.obj.__class__.__qualname__} with value {self.obj!r} to either True or False!"
