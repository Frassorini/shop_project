from shop_project.application.dto.product_dto import ProductDTO
from shop_project.domain.entities.product import Product
from shop_project.infrastructure.persistence.database.models.product import (
    Product as ProductORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class ProductRepository(BaseRepository[ProductORM, ProductDTO, Product]):
    pass
