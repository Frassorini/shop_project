from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel


class TaskHandlerRegistry:
    _registry: list["Type[BaseTaskHandler[Any]]"] = []

    @classmethod
    def register(
        cls,
        use_case_type: "Type[BaseTaskHandler[Any]]",
    ) -> None:
        if use_case_type.handler_name in (item.handler_name for item in cls._registry):
            raise ValueError(
                f"Handler ident {use_case_type.handler_name} already registered"
            )

        cls._registry.append(use_case_type)

    @classmethod
    def get_map(
        cls,
    ) -> "list[Type[BaseTaskHandler[Any]]]":
        return [item for item in cls._registry]


class BaseTaskParams(BaseModel):
    pass


class NullTaskParams(BaseTaskParams):
    pass


T = TypeVar("T", bound=BaseTaskParams | None)


class BaseTaskHandler(Generic[T], ABC):
    handler_name: str
    task_params_type: Type[T]

    @abstractmethod
    async def handle(self, task_id: UUID) -> None: ...

    def __init_subclass__(cls) -> None:
        if not cls.handler_name:
            raise ValueError

        cls.task_params_type = cls._get_generic_type()

        TaskHandlerRegistry.register(cls)

        return super().__init_subclass__()

    @classmethod
    def _get_generic_type(cls) -> Any:
        bases = cls.__bases__
        for base in getattr(cls, "__orig_bases__", ()):
            args = getattr(base, "__args__", None)
            if not args:
                continue
            if not len(args) == 1:
                raise RuntimeError("Generic has not two types")
            type_ = args[0]
            if isinstance(type_, TypeVar):
                raise RuntimeError("Generic type is lost")
            return type_
        raise RuntimeError("Generic type is not found in generic base")
