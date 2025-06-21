from typing import Any, TypeVar

from application.resource_loader.p_attribute_provider import PAttributeProvider

ModelType = TypeVar('ModelType')

class LoadQuery():
    def __init__(
        self,
        model_type: type,
        attribute_provider: PAttributeProvider,
    ) -> None:
        self.model_type: type = model_type
        self.attribute_provider: PAttributeProvider = attribute_provider
        self.result: list[Any] = []
        self.is_loaded: bool = False
