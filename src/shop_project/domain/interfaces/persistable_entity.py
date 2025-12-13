from abc import ABC
from typing import Any, Self

from shop_project.shared.identity_mixin import IdentityMixin


class PersistableEntity(IdentityMixin, ABC):
    @classmethod
    def load(cls, *args: Any, **kwargs: Any) -> Self:
        raise NotImplementedError
