from decimal import Decimal
from pydantic import BaseModel


class CreateCustomerOrderItemSchema(BaseModel):
    store_item_id: str
    amount: int


class CreateCustomerOrderSchema(BaseModel):
    customer_id: str
    store_id: str
    
    items: list[CreateCustomerOrderItemSchema]


class CustomerOrderItemSchema(BaseModel):
    store_item_id: str
    amount: int
    price: Decimal


class CustomerOrderSchema(BaseModel):
    entity_id: str
    
    customer_id: str
    store_id: str
    
    state: str
    
    items: list[CustomerOrderItemSchema]