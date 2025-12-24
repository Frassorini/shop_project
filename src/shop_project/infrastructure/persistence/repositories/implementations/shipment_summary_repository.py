from shop_project.application.dto.shipment_summary_dto import ShipmentSummaryDTO
from shop_project.domain.entities.shipment_summary import ShipmentSummary
from shop_project.infrastructure.persistence.database.models.shipment_summary import (
    ShipmentSummary as ShipmentSummaryORM,
    ShipmentSummaryItem as ShipmentSummaryItemORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
    ChildDescriptor,
)


class ShipmentSummaryRepository(
    BaseRepository[ShipmentSummaryORM, ShipmentSummaryDTO, ShipmentSummary]
):
    child_descriptors = [
        ChildDescriptor(
            child_orm=ShipmentSummaryItemORM,
            parent_dto_child_container_field_name="items",
            child_dto_parent_reference_field_name="parent_id",
            child_dto_other_pk_field_names=["product_id"],
        ),
    ]
