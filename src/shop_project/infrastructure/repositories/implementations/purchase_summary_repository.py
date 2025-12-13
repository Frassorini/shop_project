from shop_project.application.dto.purchase_summary_dto import PurchaseSummaryDTO
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.infrastructure.database.models.purchase_summary import (
    PurchaseSummary as PurchaseSummaryORM,
    PurchaseSummaryItem as PurchaseSummaryItemORM,
)
from shop_project.infrastructure.repositories.base_repository import (
    BaseRepository,
    ChildDescriptor,
)


class PurchaseSummaryRepository(
    BaseRepository[PurchaseSummaryORM, PurchaseSummaryDTO, PurchaseSummary]
):
    child_descriptors = [
        ChildDescriptor(
            child_orm=PurchaseSummaryItemORM,
            parent_dto_child_container_field_name="items",
            child_dto_parent_reference_field_name="parent_id",
            child_dto_other_pk_field_names=["product_id"],
        ),
    ]
