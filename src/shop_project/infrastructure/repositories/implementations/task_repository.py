from shop_project.application.dto.task_dto import TaskDTO
from shop_project.infrastructure.database.models.task import Task as TaskORM
from shop_project.infrastructure.entities.task import Task
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository[TaskORM, TaskDTO, Task]):
    pass
