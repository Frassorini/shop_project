from dataclasses import dataclass
from enum import Enum
from typing import Any, Self
from uuid import UUID

from shop_project.domain.exceptions import DomainException
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.stock_item import StockItem
from shop_project.shared.base_state_machine import BaseStateMachine
from shop_project.shared.p_snapshotable import PSnapshotable


@dataclass(frozen=True)
class PurchaseActiveItem(StockItem, PSnapshotable):
    product_id: UUID
    amount: int

    def __post_init__(self) -> None:
        self._validate()

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "amount": self.amount,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(
            product_id=snapshot["product_id"],
            amount=snapshot["amount"],
        )

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

    @property
    def state(self) -> PurchaseActiveState:
        return self._state_machine.state

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(
            snapshot["entity_id"],
            snapshot["customer_id"],
            snapshot["escrow_account_id"],
            [PurchaseActiveItem.from_dict(item) for item in snapshot["items"]],
        )
        obj._state_machine = PurchaseActiveStateMachine(
            PurchaseActiveState(snapshot["state"])
        )
        return obj

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "customer_id": self.customer_id,
            "escrow_account_id": self.escrow_account_id,
            "state": self.state.value,
            "items": [item.to_dict() for item in self._items.values()],
        }

    def _validate_item(self, item: PurchaseActiveItem) -> None:
        if item.product_id in self._items:
            raise DomainException("Item already added")

    def get_item(self, product_id: UUID) -> PurchaseActiveItem:
        return self._items[product_id]

    def get_items(self) -> list[PurchaseActiveItem]:
        return list(self._items.values())

    def finalize(self) -> None:
        self._state_machine.try_transition_to(PurchaseActiveState.FINALIZED)

    def is_finalized(self) -> bool:
        return self.state == PurchaseActiveState.FINALIZED

    def is_active(self) -> bool:
        return self.state == PurchaseActiveState.ACTIVE
