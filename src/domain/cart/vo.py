from dataclasses import dataclass

from shared.entity_id import EntityId


@dataclass(frozen=True)
class CartItem:
    store_item_id: EntityId
    amount: int