from typing import Protocol
from shared.identity_mixin import PIdentity
from shared.p_snapshotable import PSnapshotable


class PAggregate(PSnapshotable, PIdentity, Protocol):
    pass