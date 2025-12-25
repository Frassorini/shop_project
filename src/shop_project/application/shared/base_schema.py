from abc import ABC
from typing import Any, Self

from pydantic import BaseModel
from pydantic.config import ConfigDict


class BaseSchema(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        raise NotImplementedError
