from shop_project.application.dto.purchase_active_dto import PurchaseActiveDTO
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.infrastructure.persistence.database.models.purchase_active import (
    PurchaseActive as PurchaseActiveORM,
    PurchaseActiveItem as PurchaseActiveItemORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
    ChildDescriptor,
)


class PurchaseActiveRepository(
    BaseRepository[PurchaseActiveORM, PurchaseActiveDTO, PurchaseActive]
):
    child_descriptors = [
        ChildDescriptor(
            child_orm=PurchaseActiveItemORM,
            parent_dto_child_container_field_name="items",
            child_dto_parent_reference_field_name="parent_id",
            child_dto_other_pk_field_names=["product_id"],
        ),
    ]
