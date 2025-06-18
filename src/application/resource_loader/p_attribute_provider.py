from typing import Protocol
from typing import Generic, TypeVar

ExtractedAttributeType = TypeVar('ExtractedAttributeType')

class PAttributeProvider(Protocol, Generic[ExtractedAttributeType]):
    attribute_name: str
    def get(self) -> list[ExtractedAttributeType]:
        ...