from application.customer_order_service import CustomerOrderService
from application.dtos import OrderDTO, OrderItemDTO
from application.interfaces.interfaces import PUnitOfWork


class MockUnitOfWork(PUnitOfWork):
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True




