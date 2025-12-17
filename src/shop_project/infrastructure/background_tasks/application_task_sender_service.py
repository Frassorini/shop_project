from typing import Any

from taskiq import AsyncBroker
from taskiq.decor import AsyncTaskiqDecoratedTask

from shop_project.infrastructure.entities.task import Task


class TaskSender:
    def __init__(self, broker: AsyncBroker) -> None:
        self.broker: AsyncBroker = broker

    async def send(self, task: Task) -> None:
        taskiq_task: AsyncTaskiqDecoratedTask[Any, Any] | None = self.broker.find_task(
            task.handler
        )

        if not taskiq_task:
            raise Exception(f"Task {task.handler} not found")

        sended = await taskiq_task.kiq(task.entity_id)
