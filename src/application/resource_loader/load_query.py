from typing import Generic, Type, TypeVar

from application.resource_loader.p_attribute_provider import PAttributeProvider

ModelType = TypeVar('ModelType')
ExtractedAttributeType = TypeVar('ExtractedAttributeType')

class LoadQuery(Generic[ModelType, ExtractedAttributeType]):
    def __init__(
        self,
        model_type: Type[ModelType],
        attribute_provider: PAttributeProvider[ExtractedAttributeType],
    ) -> None:
        self.model_type: Type[ModelType] = model_type
        self.attribute_provider: PAttributeProvider[ExtractedAttributeType] = attribute_provider
        self.result: list[ModelType] = []
        self.is_loaded: bool = False
