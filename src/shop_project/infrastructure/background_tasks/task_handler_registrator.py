from typing import Annotated, Awaitable, Callable, ParamSpec, Type, TypeVar
from uuid import UUID

from dishka.async_container import AsyncContainer
from taskiq import AsyncBroker, Context, TaskiqDepends

from shop_project.application.tasks.base_task_handler import (
    BaseTaskHandler,
    BaseTaskParams,
    TaskHandlerRegistry,
)
from shop_project.application.tasks.init_background_service_registry import (
    init_background_service_registry,
)

init_background_service_registry()


P = ParamSpec("P")
T = TypeVar("T")


def construct_handler_callback(
    use_case_type: Type[BaseTaskHandler[BaseTaskParams]],
) -> Callable[..., Awaitable[None]]:
    async def _inner(
        task_id: UUID, context: Annotated[Context, TaskiqDepends()]
    ) -> None:
        container = context.state.get("di_container")
        if not isinstance(container, AsyncContainer):
            raise ValueError("Container is not AsyncContainer")
        async with container() as ctx:
            use_case = await ctx.get(use_case_type)
        await use_case.handle(task_id=task_id)

    return _inner


def register_background_tasks(
    broker: AsyncBroker,
) -> None:
    for use_case_type in TaskHandlerRegistry.get_map():
        broker.register_task(
            task_name=use_case_type.handler_name,
            func=construct_handler_callback(use_case_type),
            retry_on_error=True,
        )
