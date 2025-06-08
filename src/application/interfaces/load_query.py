from typing import Generic, Protocol, Type, TypeVar

from application.interfaces.p_criteria_provider import PCriteriaProvider


T = TypeVar('T')

class LoadQuery(Generic[T]):
    def __init__(self, model_type: Type[T], id_provider: PCriteriaProvider) -> None:
        self.model_type = model_type
        self.id_provider = id_provider
        self.result: list[T] = []
        self.is_loaded = False

    