from shop_project.application.dto.manager_dto import ManagerDTO
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.database.models.manager import Manager as ManagerORM
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ManagerRepository(BaseRepository[ManagerORM, ManagerDTO, Manager]):
    pass
