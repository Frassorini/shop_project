from dataclasses import dataclass


@dataclass(frozen=True)
class OrderItemDTO:
    store_item_id: int
    amount: int
    

@dataclass(frozen=True)
class OrderDTO:
    customer_id: int
    state: str
    items: list[OrderItemDTO]

