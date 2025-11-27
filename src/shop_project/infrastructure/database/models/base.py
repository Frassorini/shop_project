from abc import abstractmethod
from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    @abstractmethod
    def repopulate(self, *args: Any, **kw: Any) -> None: ...
