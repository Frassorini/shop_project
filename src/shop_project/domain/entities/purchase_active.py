from dataclasses import dataclass
from enum import Enum
from typing import Self
from uuid import UUID

from shop_project.domain.exceptions import DomainException
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.stock_item import StockItem
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class PurchaseActiveItem(StockItem):
    product_id: UUID
    amount: int

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.amount <= 0:
            raise DomainException("Amount must be > 0")


class PurchaseActiveState(Enum):
    ACTIVE = "ACTIVE"
    FINALIZED = "FINALIZED"


class PurchaseActiveStateMachine(BaseStateMachine[PurchaseActiveState]):
    _transitions = {
        PurchaseActiveState.ACTIVE: [PurchaseActiveState.FINALIZED],
    }


class PurchaseActive(PersistableEntity):
    entity_id: UUID
    customer_id: UUID
    escrow_account_id: UUID

    _items: dict[UUID, PurchaseActiveItem]
    _state_machine: PurchaseActiveStateMachine

    def __init__(
        self,
        entity_id: UUID,
        customer_id: UUID,
        escrow_account_id: UUID,
        items: list[PurchaseActiveItem],
    ) -> None:
        self.entity_id: UUID = entity_id

        self.customer_id: UUID = customer_id
        self.escrow_account_id: UUID = escrow_account_id

        self._items: dict[UUID, PurchaseActiveItem] = {}

        self._state_machine = PurchaseActiveStateMachine(PurchaseActiveState.ACTIVE)

        for item in items:
            self._validate_item(item)
            self._items[item.product_id] = item

    @classmethod
    def load(
        cls,
        entity_id: UUID,
        customer_id: UUID,
        escrow_account_id: UUID,
        items: list[PurchaseActiveItem],
        state: PurchaseActiveState,
    ) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.customer_id = customer_id
        obj.escrow_account_id = escrow_account_id
        obj._items = {item.product_id: item for item in items}
        obj._state_machine = PurchaseActiveStateMachine(state)

        return obj

    @property
    def state(self) -> PurchaseActiveState:
        return self._state_machine.state

    def _validate_item(self, item: PurchaseActiveItem) -> None:
        if item.product_id in self._items:
            raise DomainException("Item already added")

    def get_item(self, product_id: UUID) -> PurchaseActiveItem:
        return self._items[product_id]

    @property
    def items(self) -> list[PurchaseActiveItem]:
        return sorted(self._items.values(), key=lambda item: item.product_id)

    def get_items(self) -> list[PurchaseActiveItem]:
        return list(self._items.values())

    def finalize(self) -> None:
        self._state_machine.try_transition_to(PurchaseActiveState.FINALIZED)

    def is_finalized(self) -> bool:
        return self.state == PurchaseActiveState.FINALIZED

    def is_active(self) -> bool:
        return self.state == PurchaseActiveState.ACTIVE
