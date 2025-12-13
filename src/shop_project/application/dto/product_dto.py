from decimal import Decimal
from typing import Self
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.domain.entities.product import Product


class ProductDTO(BaseDTO[Product]):
    entity_id: UUID
    name: str
    amount: int
    price: Decimal

    @classmethod
    def to_dto(cls, domain_object: Product) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            name=domain_object.name,
            amount=domain_object.amount,
            price=domain_object.price,
        )

    def to_domain(self) -> Product:
        return Product.load(
            entity_id=self.entity_id,
            name=self.name,
            amount=self.amount,
            price=self.price,
        )
