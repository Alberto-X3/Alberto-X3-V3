__all__ = (
    "event_loop",
    "Thread",
    "LockDeco",
    "gather_any",
    "run_in_thread",
    "semaphore_gather",
    "run_as_task",
)

from asyncio import (
    Event,
    Lock,
    Semaphore,
    create_task,
    gather,
    get_event_loop,
    get_running_loop,
)
from functools import partial, update_wrapper, wraps
from threading import Thread as t_Thread
from typing import TYPE_CHECKING
from .contants import MISSING
from .errors import GatherAnyError

if TYPE_CHECKING:
    from typing import Awaitable, NoReturn, ParamSpec, TypeVar

    T = TypeVar("T")
    P = ParamSpec("P")


event_loop = get_event_loop()


class Thread(t_Thread):
    _return = MISSING, MISSING

    def __init__(self, func, loop):
        super().__init__()

        self._func = func
        self._event = Event()
        self._loop = loop

    async def wait(self):
        """
        Returns
        -------
        tuple[Literal[True], T] | tuple[Literal[False], Exception]
            A tuple containing a boolean and the return from the function if ``True``,
            otherwise the exception which was raised.
        """
        await self._event.wait()
        return self._return

    def run(self, *args, **kwargs):
        try:
            self._return = True, self._func(*args, **kwargs)
        except Exception as e:
            self._return = False, e
        self._loop.call_soon_threadsafe(self._event.set)


class LockDeco:
    def __init__(self, func):
        self.lock = Lock()
        self.func = func
        update_wrapper(self, func)

    async def __call__(self, *args, **kwargs):
        async with self.lock:
            return await self.func(*args, **kwargs)


async def gather_any(*coroutines):
    """
    Parameters
    ----------
    coroutines: Awaitable[T]
        Coroutines to execute.

    Returns
    -------
    tuple[int, T]
        The position of the coroutine to finish first with its return value.

    Raises
    ------
    GatherAnyError
        If an exception was raised during gathering.
    """
    event = Event()
    res: list[tuple[int, bool, T]] = []

    async def inner(idx: int, coro: Awaitable[T]) -> NoReturn:
        try:
            res.append((idx, True, await coro))
        except Exception as e:
            res.append((idx, False, e))
        event.set()

    tasks = [create_task(inner(i, c)) for i, c in enumerate(coroutines)]
    await event.wait()

    for task in tasks:
        if not task.done():
            task.cancel()

    index, ok, value = res[0]  # the first result
    if not ok:
        raise GatherAnyError(index, value)
    else:
        return index, value


async def run_in_thread(func, *args, **kwargs):
    """
    Parameters
    ----------
    func: Callable[P, T]
        The function to run in a thread.
    args: P.args
        The arguments for the function.
    kwargs: P.kwargs
        The keyword-arguments for the function.

    Returns
    -------
    T
        The return from the function.

    Raises
    ------
    Exception
        Any exceptions which may be raised.
    """
    thread = Thread(partial(func, *args, **kwargs), get_running_loop())
    thread.start()
    ok, result = await thread.wait()
    if not ok:
        raise result
    else:
        return result


async def semaphore_gather(n, /, *tasks):
    """
    Runs multiple tasks at once and returns their returns.

    Parameters
    ----------
    n: int
        The maximum amount of tasks to run simultaneously.
    tasks: Awaitable[T]
        The tasks to execute.

    Returns
    -------
    list[T]
        The return values from the tasks.
    """
    semaphore = Semaphore(n)

    async def inner(t: Awaitable[T]) -> T:
        async with semaphore:
            return await t

    return list(await gather(*map(inner, tasks)))


def run_as_task(func):
    """
    Parameters
    ----------
    func: Callable[P, T]
        The coroutine to execute.

    Returns
    -------
    Callable[P, T]
        The wrapped function.
    """

    @wraps(func)
    async def inner(*args: P.args, **kwargs: P.kwargs):
        create_task(func(*args, **kwargs))

    return inner
