from decimal import Decimal

from pydantic import BaseModel


class CreatePurchaseActiveItemSchema(BaseModel):
    product_id: str
    amount: int


class CreatePurchaseActiveSchema(BaseModel):
    customer_id: str
    store_id: str

    items: list[CreatePurchaseActiveItemSchema]


class PurchaseActiveItemSchema(BaseModel):
    product_id: str
    amount: int
    price: Decimal


class PurchaseActiveSchema(BaseModel):
    entity_id: str

    customer_id: str
    store_id: str

    state: str

    items: list[PurchaseActiveItemSchema]
