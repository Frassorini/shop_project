from contextlib import AbstractAsyncContextManager
from typing import AsyncGenerator, Callable

from dishka import BaseScope, Component, Provider, Scope, alias, provide
from taskiq import AsyncBroker

from shop_project.application.interfaces.interface_task_factory import ITaskFactory
from shop_project.application.interfaces.interface_task_sender import ITaskSender
from shop_project.infrastructure.background_tasks.application_task_factory import (
    TaskFactory,
)
from shop_project.infrastructure.background_tasks.application_task_sender_service import (
    TaskSender,
)


class BrokerProvider(Provider):
    scope = Scope.APP

    def __init__(
        self,
        database_ctx: Callable[[], AbstractAsyncContextManager[AsyncBroker]],
        *,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ):
        super().__init__(scope, component)

        self.broker_ctx = database_ctx

    @provide(scope=Scope.APP)
    async def broker(self) -> AsyncGenerator[AsyncBroker, None]:
        ctx = self.broker_ctx()
        res = await ctx.__aenter__()  # вручную войти
        try:
            yield res
        finally:
            await ctx.__aexit__(None, None, None)

    @provide
    async def task_sender(self, broker: AsyncBroker) -> TaskSender:
        return TaskSender(broker)

    @provide
    async def task_factory(self) -> TaskFactory:
        return TaskFactory()

    task_sender_proto = alias(TaskSender, provides=ITaskSender)
    task_factory_proto = alias(TaskFactory, provides=ITaskFactory)
