from typing import Protocol
from shop_project.shared.identity_mixin import PIdentity
from shop_project.shared.p_snapshotable import PSnapshotable


class PAggregate(PSnapshotable, PIdentity, Protocol):
    pass