from enum import Enum


class CustomerOrderState(Enum):
    PENDING = 'PENDING'
    RESERVED = 'RESERVED'
    PAID = 'PAID'
    RECEIVED = 'RECEIVED'
    CANCELLED = 'CANCELLED'