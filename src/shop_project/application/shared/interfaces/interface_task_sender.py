from typing import Protocol

from shop_project.application.entities.task import Task


class ITaskSender(Protocol):
    async def send(self, task: Task) -> None: ...
