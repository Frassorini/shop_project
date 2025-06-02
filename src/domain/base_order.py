from enum import Enum
from functools import wraps

from domain.exceptions import StateException


class OrderState(Enum):
    ...


class Order():
    @staticmethod
    def _state_required(allowed_states: list[OrderState]):
        def wrapped(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if hasattr(args[0], 'state') and args[0].state in allowed_states:
                    return func(*args, **kwargs)
                else:
                    raise StateException('Invalid state to perform action')
            return wrapper
        return wrapped