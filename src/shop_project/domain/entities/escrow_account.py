from decimal import Decimal
from enum import Enum
from typing import Self
from uuid import UUID

from shop_project.domain.exceptions import DomainException
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.shared.base_state_machine import BaseStateMachine


class EscrowAccountState(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    PAYMENT_CANCELLED = "CANCELLED"
    READY_FOR_REFUND = "READY_FOR_REFUND"
    REFUNDING = "REFUNDING"
    FINALIZED = "FINALIZED"


class EscrowAccountStateMachine(BaseStateMachine[EscrowAccountState]):
    _transitions = {
        EscrowAccountState.PENDING: [
            EscrowAccountState.PAID,
            EscrowAccountState.PAYMENT_CANCELLED,
        ],
        EscrowAccountState.PAID: [
            EscrowAccountState.READY_FOR_REFUND,
            EscrowAccountState.FINALIZED,
        ],
        EscrowAccountState.PAYMENT_CANCELLED: [EscrowAccountState.FINALIZED],
        EscrowAccountState.READY_FOR_REFUND: [EscrowAccountState.REFUNDING],
        EscrowAccountState.REFUNDING: [EscrowAccountState.FINALIZED],
        EscrowAccountState.FINALIZED: [],
    }


class EscrowAccount(PersistableEntity):
    entity_id: UUID
    total_amount: Decimal
    _state_machine: EscrowAccountStateMachine

    def __init__(self, entity_id: UUID, total_amount: Decimal) -> None:
        if total_amount <= 0:
            raise DomainException("Total amount must be positive")
        self.entity_id = entity_id
        self.total_amount: Decimal = total_amount
        self._state_machine = EscrowAccountStateMachine(EscrowAccountState.PENDING)

    @classmethod
    def _load(
        cls, entity_id: UUID, total_amount: Decimal, state: EscrowAccountState
    ) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.total_amount = total_amount
        obj._state_machine = EscrowAccountStateMachine(state)

        return obj

    @property
    def state(self) -> EscrowAccountState:
        return self._state_machine.state

    def mark_as_paid(self) -> None:
        self._state_machine.try_transition_to(EscrowAccountState.PAID)

    def cancel(self) -> None:
        self._state_machine.try_transition_to(EscrowAccountState.PAYMENT_CANCELLED)

    def mark_as_ready_for_refund(self) -> None:
        self._state_machine.try_transition_to(EscrowAccountState.READY_FOR_REFUND)

    def begin_refund(self) -> None:
        self._state_machine.try_transition_to(EscrowAccountState.REFUNDING)

    def finalize(self) -> None:
        self._state_machine.try_transition_to(EscrowAccountState.FINALIZED)

    def is_pending(self) -> bool:
        return self.state == EscrowAccountState.PENDING

    def is_paid(self) -> bool:
        return self.state == EscrowAccountState.PAID

    def is_cancelled(self) -> bool:
        return self.state == EscrowAccountState.PAYMENT_CANCELLED

    def is_ready_for_refund(self) -> bool:
        return self.state == EscrowAccountState.READY_FOR_REFUND

    def is_refunding(self) -> bool:
        return self.state == EscrowAccountState.REFUNDING

    def is_finalized(self) -> bool:
        return self.state == EscrowAccountState.FINALIZED
