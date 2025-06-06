from enum import Enum


class SupplierOrderState(Enum):
    PENDING = 'PENDING'
    DEPARTED = 'DEPARTED'
    RECEIVED = 'RECEIVED'
    CANCELLED = 'CANCELLED'