from abc import ABC

from shop_project.shared.identity_mixin import IdentityMixin


class PersistableEntity(IdentityMixin, ABC):
    pass
