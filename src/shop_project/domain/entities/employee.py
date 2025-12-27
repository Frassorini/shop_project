from enum import Enum
from typing import Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.subject import Subject
from shop_project.shared.base_state_machine import BaseStateMachine


class EmployeeState(Enum):
    UNAUTHORIZED = "UNAUTHORIZED"
    AUTHORIZED = "AUTHORIZED"


class EmployeeStateMachine(BaseStateMachine[EmployeeState]):
    _transitions = {
        EmployeeState.UNAUTHORIZED: [EmployeeState.AUTHORIZED],
        EmployeeState.AUTHORIZED: [EmployeeState.UNAUTHORIZED],
    }


class Employee(Subject, PersistableEntity):
    entity_id: UUID
    name: str
    _state_machine: EmployeeStateMachine

    def __init__(self, entity_id: UUID, name: str) -> None:
        self.entity_id: UUID = entity_id
        self.name: str = name
        self._state_machine = EmployeeStateMachine(EmployeeState.UNAUTHORIZED)

    @classmethod
    def load(cls, entity_id: UUID, name: str, state: EmployeeState) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.name = name
        obj._state_machine = EmployeeStateMachine(state)

        return obj

    @property
    def state(self) -> EmployeeState:
        return self._state_machine.state

    def authorize(self) -> None:
        self._state_machine.try_transition_to(EmployeeState.AUTHORIZED)

    def unauthorize(self) -> None:
        self._state_machine.try_transition_to(EmployeeState.UNAUTHORIZED)

    def is_authorized(self) -> bool:
        return self._state_machine.state == EmployeeState.AUTHORIZED
