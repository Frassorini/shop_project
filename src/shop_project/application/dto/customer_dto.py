from datetime import datetime
from decimal import Decimal
from shop_project.application.dto.base_dto import BaseDTO


class CustomerDTO(BaseDTO):
    entity_id: str
    name: str