from shop_project.application.shared.dto.customer_dto import CustomerDTO
from shop_project.domain.entities.customer import Customer
from shop_project.infrastructure.persistence.database.models.customer import (
    Customer as CustomerORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class CustomerRepository(BaseRepository[CustomerORM, CustomerDTO, Customer]):
    pass
