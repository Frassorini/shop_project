from decimal import Decimal
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class ProductDTO(BaseDTO):
    entity_id: UUID
    name: str
    amount: int
    price: Decimal
