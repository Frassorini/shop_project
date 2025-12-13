from shop_project.application.dto.shipment_dto import ShipmentDTO
from shop_project.domain.entities.shipment import Shipment
from shop_project.infrastructure.database.models.shipment import (
    Shipment as ShipmentORM,
    ShipmentItem as ShipmentItemORM,
)
from shop_project.infrastructure.repositories.base_repository import (
    BaseRepository,
    ChildDescriptor,
)


class ShipmentRepository(BaseRepository[ShipmentORM, ShipmentDTO, Shipment]):
    child_descriptors = [
        ChildDescriptor(
            child_orm=ShipmentItemORM,
            parent_dto_child_container_field_name="items",
            child_dto_parent_reference_field_name="parent_id",
            child_dto_other_pk_field_names=["product_id"],
        ),
    ]
