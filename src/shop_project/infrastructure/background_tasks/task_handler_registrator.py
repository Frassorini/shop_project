from typing import Annotated, Awaitable, Callable, ParamSpec, Type, TypeVar
from uuid import UUID

from dishka.async_container import AsyncContainer
from taskiq import AsyncBroker, Context, TaskiqDepends

from shop_project.application.background.base_task_handler import (
    BaseTaskHandler,
    BaseTaskParams,
    TaskHandlerRegistry,
)
from shop_project.application.background.init_task_handler_registry import (
    init_task_handler_registry,
)
from shop_project.application.exceptions import RetryException
from shop_project.infrastructure.background_tasks.on_task_fail_actions import (
    log_message_taskiq,
)

init_task_handler_registry()


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
        try:
            async with container() as ctx:
                use_case = await ctx.get(use_case_type)
            await use_case.handle(task_id=task_id)
        except RetryException:
            raise
        except Exception as e:
            await log_message_taskiq(context.message, e)
            raise RetryException from e

    return _inner


def register_background_tasks(
    broker: AsyncBroker,
) -> None:
    for use_case_type in TaskHandlerRegistry.get_map():
        broker.register_task(
            task_name=use_case_type.handler_name,
            func=construct_handler_callback(use_case_type),
        )
