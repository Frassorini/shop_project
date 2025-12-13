from abc import ABC
from typing import Any, Generic, Self, TypeVar, Unpack
from uuid import UUID

from pydantic import BaseModel
from pydantic.config import ConfigDict

from shop_project.domain.interfaces.persistable_entity import PersistableEntity

T = TypeVar("T", bound=PersistableEntity)


class DTODynamicRegistry:
    map: Any = {}

    @classmethod
    def register(cls, domain_type: Any, dto_type: Any) -> None:
        cls.map[domain_type] = dto_type

    @classmethod
    def get(cls, domain_type: Any) -> Any:
        return cls.map[domain_type]


class BaseVODTO(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True)


class BaseDTO(BaseModel, Generic[T]):
    entity_id: UUID
    model_config = ConfigDict(from_attributes=True)

    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]):
        if cls.is_needed_to_register():
            DTODynamicRegistry.register(cls._get_one_generic_type(), cls)

        return super().__init_subclass__(**kwargs)

    @classmethod
    def _get_one_generic_type(cls) -> Any:
        bases = cls.__bases__
        for base in bases:
            meta = getattr(base, "__pydantic_generic_metadata__", None)
            if not meta:
                continue
            args = meta.get("args")
            if not args:
                continue
            if not len(args) == 1:
                raise RuntimeError("Generic has more than one type")
            type_ = args[0]
            if isinstance(type_, TypeVar):
                raise RuntimeError("Generic type is lost")
            return type_
        raise RuntimeError("Generic type is not found in generic base")

    def model_post_init(self, context: Any, /) -> None:
        if not self._get_one_generic_type():
            raise ValueError("Generic type is not set")

    @classmethod
    def to_dto(cls, domain_object: T) -> Self:
        return cls.model_validate(domain_object, from_attributes=True)

    def to_domain(self) -> T:
        return self._get_one_generic_type().load(self.model_dump())

    @classmethod
    def is_needed_to_register(cls) -> bool:
        meta = getattr(cls, "__pydantic_generic_metadata__", None)
        if not meta:
            raise RuntimeError("Generic metadata is not found")

        if meta.get("args"):
            return True
        return False
