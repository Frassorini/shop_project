from decimal import Decimal
from enum import Enum
from typing import Any, Self
from uuid import UUID

from shop_project.domain.exceptions import DomainException
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.shared.base_state_machine import BaseStateMachine


class EscrowState(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PAYMENT_CANCELLED = "CANCELLED"
    READY_FOR_REFUND = "READY_FOR_REFUND"
    REFUNDING = "REFUNDING"
    FINALIZED = "FINALIZED"


class EscrowStateMachine(BaseStateMachine[EscrowState]):
    _transitions = {
        EscrowState.PENDING: [EscrowState.PAID, EscrowState.PAYMENT_CANCELLED],
        EscrowState.PAID: [EscrowState.READY_FOR_REFUND, EscrowState.FINALIZED],
        EscrowState.PAYMENT_CANCELLED: [EscrowState.FINALIZED],
        EscrowState.READY_FOR_REFUND: [EscrowState.REFUNDING],
        EscrowState.REFUNDING: [EscrowState.FINALIZED],
        EscrowState.FINALIZED: [],
    }


class EscrowAccount(PersistableEntity):
    def __init__(self, entity_id: UUID, total_amount: Decimal) -> None:
        if total_amount <= 0:
            raise DomainException("Total amount must be positive")
        self.entity_id = entity_id
        self.total_amount: Decimal = total_amount
        self._state_machine = EscrowStateMachine(EscrowState.PENDING)

    @property
    def state(self) -> EscrowState:
        return self._state_machine.state

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "total_amount": self.total_amount,
            "state": self.state.value,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj.entity_id = snapshot["entity_id"]
        obj.total_amount = snapshot["total_amount"]
        obj._state_machine = EscrowStateMachine(EscrowState(snapshot["state"]))
        return obj

    def mark_as_paid(self) -> None:
        self._state_machine.try_transition_to(EscrowState.PAID)

    def cancel(self) -> None:
        self._state_machine.try_transition_to(EscrowState.PAYMENT_CANCELLED)

    def mark_as_ready_for_refund(self) -> None:
        self._state_machine.try_transition_to(EscrowState.READY_FOR_REFUND)

    def begin_refund(self) -> None:
        self._state_machine.try_transition_to(EscrowState.REFUNDING)

    def finalize(self) -> None:
        self._state_machine.try_transition_to(EscrowState.FINALIZED)

    def is_pending(self) -> bool:
        return self.state == EscrowState.PENDING

    def is_paid(self) -> bool:
        return self.state == EscrowState.PAID

    def is_cancelled(self) -> bool:
        return self.state == EscrowState.PAYMENT_CANCELLED

    def is_ready_for_refund(self) -> bool:
        return self.state == EscrowState.READY_FOR_REFUND

    def is_refunding(self) -> bool:
        return self.state == EscrowState.REFUNDING

    def is_finalized(self) -> bool:
        return self.state == EscrowState.FINALIZED
