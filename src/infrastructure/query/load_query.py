from typing import Type

from domain.p_aggregate import PAggregate
from infrastructure.query.p_attribute_provider import PAttributeProvider

class LoadQuery():
    def __init__(
        self,
        model_type: type,
        attribute_provider: PAttributeProvider,
    ) -> None:
        self.model_type: Type[PAggregate] = model_type
        self.attribute_provider: PAttributeProvider = attribute_provider
        self.result: list[PAggregate] = []
        self.is_loaded: bool = False
