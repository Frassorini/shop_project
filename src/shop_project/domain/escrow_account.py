from decimal import Decimal
from typing import Any, Self
from enum import Enum
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.shared.entity_id import EntityId
from shop_project.domain.exceptions import DomainException
from shop_project.shared.base_state_machine import BaseStateMachine


class EscrowState(Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    REFUNDING = 'REFUNDING'
    FINALIZED = 'FINALIZED'


class EscrowStateMachine(BaseStateMachine[EscrowState]):
    _transitions = {
        EscrowState.PENDING: [EscrowState.PAID, EscrowState.FINALIZED],
        EscrowState.PAID: [EscrowState.REFUNDING, EscrowState.FINALIZED],
        EscrowState.REFUNDING: [EscrowState.FINALIZED],
        EscrowState.FINALIZED: [],
    }


class EscrowAccount(BaseAggregate):
    def __init__(self, entity_id: EntityId, total_amount: Decimal) -> None:
        if total_amount <= 0:
            raise DomainException("Total amount must be positive")
        self._entity_id = entity_id
        self._purchase_active_id: EntityId | None = None
        self.total_amount: Decimal = total_amount
        self._state_machine = EscrowStateMachine(EscrowState.PENDING)

    @property
    def state(self) -> EscrowState:
        return self._state_machine.state
    
    @property
    def purchase_active_id(self) -> EntityId | None:
        return self._purchase_active_id

    def to_dict(self) -> dict[str, Any]:
        return {
            'entity_id': self.entity_id.value,
            'purchase_active_id': self._purchase_active_id.value if self._purchase_active_id else None,
            'total_amount': self.total_amount,
            'state': self.state.value,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls.__new__(cls)
        obj._entity_id = EntityId(snapshot['entity_id'])
        obj._purchase_active_id = EntityId(snapshot['purchase_active_id']) if snapshot['purchase_active_id'] else None
        obj.total_amount = snapshot['total_amount']
        obj._state_machine = EscrowStateMachine(EscrowState(snapshot['state']))
        return obj
    
    def attach_to_purchase(self, purchase_active_id: EntityId) -> None:
        if self._purchase_active_id is not None:
            raise DomainException("Escrow account is already attached to a purchase")
        
        if self.state != EscrowState.PENDING:
            raise DomainException("Escrow account is not pending")
        self._purchase_active_id = purchase_active_id
    
    def mark_as_paid(self) -> None:
        self._state_machine.try_transition_to(EscrowState.PAID)

    def finalize(self) -> None:
        self._state_machine.try_transition_to(EscrowState.FINALIZED)
        self._purchase_active_id = None
        
    def begin_refund(self) -> None:
        self._state_machine.try_transition_to(EscrowState.REFUNDING)
        self._purchase_active_id = None
    
    def is_pending(self) -> bool:
        return self.state == EscrowState.PENDING
    
    def is_paid(self) -> bool:
        return self.state == EscrowState.PAID
    
    def is_refunding(self) -> bool:
        return self.state == EscrowState.REFUNDING
    
    def is_finalized(self) -> bool:
        return self.state == EscrowState.FINALIZED
