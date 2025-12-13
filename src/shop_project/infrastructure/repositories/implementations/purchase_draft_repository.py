from shop_project.application.dto.purchase_draft_dto import PurchaseDraftDTO
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.infrastructure.database.models.purchase_draft import (
    PurchaseDraft as PurchaseDraftORM,
    PurchaseDraftItem as PurchaseDraftItemORM,
)
from shop_project.infrastructure.repositories.base_repository import (
    BaseRepository,
    ChildDescriptor,
)


class PurchaseDraftRepository(
    BaseRepository[PurchaseDraftORM, PurchaseDraftDTO, PurchaseDraft]
):
    child_descriptors = [
        ChildDescriptor(
            child_orm=PurchaseDraftItemORM,
            parent_dto_child_container_field_name="items",
            child_dto_parent_reference_field_name="parent_id",
            child_dto_other_pk_field_names=["product_id"],
        ),
    ]
