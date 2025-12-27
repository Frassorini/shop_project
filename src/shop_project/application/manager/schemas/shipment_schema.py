from uuid import UUID

from shop_project.application.shared.base_schema import BaseSchema


class ShipmentItemSchema(BaseSchema):
    product_id: UUID
    amount: int


class ShipmentSchema(BaseSchema):
    entity_id: UUID
    state: str
    items: list[ShipmentItemSchema]


class CreateShipmentSchema(BaseSchema):
    items: list[ShipmentItemSchema]


class ShipmentSummaryItemSchema(BaseSchema):
    product_id: UUID
    amount: int


class ShipmentSummarySchema(BaseSchema):
    entity_id: UUID
    reason: str
    items: list[ShipmentSummaryItemSchema]
