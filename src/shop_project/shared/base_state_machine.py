from abc import ABC
from typing import Generic, TypeVar

from shop_project.domain.exceptions import StateException


T = TypeVar('T')

class BaseStateMachine(ABC, Generic[T]):
    _transitions: dict[T, list[T]]
    
    def __init__(self, initial_state: T):
        self._state: T = initial_state
    
    @property
    def state(self) -> T:
        return self._state
    
    def try_transition_to(self, to_state: T) -> None:
        if not self.can_be_transitioned_to(to_state):
            raise StateException(f'Invalid transition from {self._state} to {to_state}')
        
        self._state = to_state
    
    def can_be_transitioned_to(self, to_state: T) -> bool:
        return to_state in self._transitions[self._state]
    
    