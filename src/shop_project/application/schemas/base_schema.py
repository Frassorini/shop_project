from abc import ABC
from typing import Self

from pydantic import BaseModel
from pydantic.config import ConfigDict

from shop_project.application.dto.base_dto import BaseDTO

class BaseSchema(BaseModel, ABC):
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def create(cls, *args, **kwargs) -> Self: # type: ignore
        raise NotImplementedError