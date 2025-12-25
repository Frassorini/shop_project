from typing import Protocol

from shop_project.infrastructure.entities.task import Task


class ITaskSender(Protocol):
    async def send(self, task: Task) -> None: ...
