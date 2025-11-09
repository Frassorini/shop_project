from datetime import datetime
from decimal import Decimal
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO


class EscrowAccountDTO(BaseDTO):
    entity_id: UUID
    state: str
    total_amount: Decimal