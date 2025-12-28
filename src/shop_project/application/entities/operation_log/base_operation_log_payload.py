from typing import Any, Generic, TypeVar, Unpack

from pydantic import BaseModel, ConfigDict

from shop_project.application.entities.operation_log.operation_code import (
    OperationCodeEnum,
)

T = TypeVar("T", bound=OperationCodeEnum)


class OperationPayloadDynamicRegistry:
    map: Any = {}

    @classmethod
    def register(cls, payload_type: Any, operation_enum: OperationCodeEnum) -> None:
        cls.map[payload_type] = operation_enum

    @classmethod
    def get(cls, payload_type: Any) -> OperationCodeEnum:
        return cls.map[payload_type]


class BaseOperationLogPayload(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]):
        if cls.is_needed_to_register():
            OperationPayloadDynamicRegistry.register(cls, cls._get_one_generic_type())

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
    def is_needed_to_register(cls) -> bool:
        meta = getattr(cls, "__pydantic_generic_metadata__", None)
        if not meta:
            raise RuntimeError("Generic metadata is not found")

        if meta.get("args"):
            return True
        return False

    def get_operation_code(self) -> OperationCodeEnum:
        return OperationPayloadDynamicRegistry.get(self.__class__)

    def get_payload_json(self) -> str:
        return self.model_dump_json()
