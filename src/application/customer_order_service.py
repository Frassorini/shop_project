from application.dtos import OrderDTO, OrderItemDTO
from application.interfaces.interfaces import PUnitOfWork


class CustomerOrderService:
    def __init__(self, uow: PUnitOfWork) -> None:
        self.uow = uow
    
    def reserve_order(self, data: list[OrderItemDTO], customer_id: int) -> OrderDTO:
        with self.uow:
            # resources_container = uow.resources
            return OrderDTO(state='RESERVED', items=data, customer_id=1)