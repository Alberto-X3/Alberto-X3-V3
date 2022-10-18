from asyncio import AbstractEventLoop, Event, Lock
from threading import Thread as t_Thread
from typing import Awaitable, Callable, Literal, NoReturn, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")

event_loop: AbstractEventLoop

class Thread(t_Thread):
    _return: tuple[Literal[True], T] | tuple[Literal[False], Exception]
    _func: Callable[P, T]
    _event: Event
    _loop: AbstractEventLoop

    def __init__(self, func: Callable[P, T], loop: AbstractEventLoop): ...
    async def wait(self) -> tuple[Literal[True], T] | tuple[Literal[False], Exception]: ...
    def run(self, *args: P.args, **kwargs: P.kwargs) -> NoReturn: ...

class LockDeco:
    lock: Lock
    func: Callable[P, T]

    def __init__(self, func: Callable[P, T]): ...
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T: ...

class GatherAnyError(Exception):
    idx: int
    exception: Exception

    def __init__(self, idx: int, exception: Exception): ...

async def gather_any(*coroutines: Awaitable[T]) -> tuple[int, T]: ...
async def run_in_thread(func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T: ...
async def semaphore_gather(n: int, /, *tasks: Awaitable[T]) -> list[T]: ...
def run_as_task(func: Callable[P, T]) -> Callable[P, T]: ...
