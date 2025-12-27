from decimal import Decimal
from uuid import UUID

from shop_project.application.shared.base_schema import BaseSchema


class ProductSchema(BaseSchema):
    entity_id: UUID
    name: str
    amount: int
    price: Decimal


class ChangeProductSchema(BaseSchema):
    entity_id: UUID
    name: str
    price: Decimal


class CreateProductSchema(BaseSchema):
    name: str
    amount: int
    price: Decimal
