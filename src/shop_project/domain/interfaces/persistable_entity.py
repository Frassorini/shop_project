from abc import ABC
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.shared.p_snapshotable import PSnapshotable


class PersistableEntity(PSnapshotable, IdentityMixin, ABC):
    pass