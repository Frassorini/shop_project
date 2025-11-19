from asyncio import iscoroutinefunction
from functools import wraps
from inspect import markcoroutinefunction
from typing import TYPE_CHECKING, Callable, ParamSpec, TypeVar

if TYPE_CHECKING:
    from taskiq import AsyncTaskiqDecoratedTask
    from taskiq.abc.broker import AsyncBroker


_FuncParams = ParamSpec("_FuncParams")
_ReturnType = TypeVar("_ReturnType")


def _task_wrapper(
    func: Callable[_FuncParams, _ReturnType],
) -> Callable[_FuncParams, _ReturnType]:
    @wraps(func)
    def wrapper(*args: _FuncParams.args, **kwargs: _FuncParams.kwargs) -> _ReturnType:
        return func(*args, **kwargs)

    return wrapper


class TaskContainer:
    def __init__(self, broker: "AsyncBroker") -> None:
        self._broker = broker

    def get_task(
        self,
        func: Callable[_FuncParams, _ReturnType],
    ) -> "AsyncTaskiqDecoratedTask[_FuncParams, _ReturnType]":
        res = self._broker.find_task(func.__name__)

        if res:
            return res

        wrapped_func = _task_wrapper(func)

        if iscoroutinefunction(func):
            wrapped_func = markcoroutinefunction(wrapped_func)

        return self._broker.register_task(
            wrapped_func, task_name=func.__name__
        )  # taskiq changes func.__name__ for some unclear reason
