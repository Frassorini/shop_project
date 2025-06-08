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


def test_() -> None:
    uow = MockUnitOfWork()
    customer_order_service = CustomerOrderService(uow)


def test_reserve_order() -> None:
    uow = MockUnitOfWork()
    customer_order_service: CustomerOrderService = CustomerOrderService(uow)
    data: list[OrderItemDTO] = [OrderItemDTO(store_item_id=1, amount=1)]
    
    order: OrderDTO = customer_order_service.reserve_order(data, 1)
    
    assert order.state == 'RESERVED'

