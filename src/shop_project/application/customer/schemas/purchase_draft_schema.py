from decimal import Decimal
from typing import Self
from uuid import UUID

from shop_project.application.shared.base_schema import BaseSchema
from shop_project.application.shared.dto.product_dto import ProductDTO
from shop_project.application.shared.dto.purchase_draft_dto import PurchaseDraftDTO


class PurchaseDraftItemSchema(BaseSchema):
    product_id: UUID
    name: str | None
    amount: int
    price: Decimal | None


class PurchaseDraftSchema(BaseSchema):
    entity_id: UUID
    customer_id: UUID
    items: list[PurchaseDraftItemSchema]

    @classmethod
    def create(
        cls, purchase_draft_dto: PurchaseDraftDTO, products: list[ProductDTO]
    ) -> Self:
        items: list[PurchaseDraftItemSchema] = []
        for purchase_draft_item in purchase_draft_dto.items:
            found = False
            for product in products:
                if product.entity_id == purchase_draft_item.product_id:
                    items.append(
                        PurchaseDraftItemSchema(
                            product_id=product.entity_id,
                            name=product.name,
                            amount=purchase_draft_item.amount,
                            price=product.price,
                        )
                    )
                    found = True
                    break
            if not found:
                items.append(
                    PurchaseDraftItemSchema(
                        product_id=purchase_draft_item.product_id,
                        name=None,
                        amount=purchase_draft_item.amount,
                        price=None,
                    )
                )

        return cls(
            entity_id=purchase_draft_dto.entity_id,
            customer_id=purchase_draft_dto.customer_id,
            items=items,
        )


class NewPurchaseDraftItemSchema(BaseSchema):
    product_id: UUID
    amount: int


class SetNewPurchaseDraftItemsSchema(BaseSchema):
    items: list[NewPurchaseDraftItemSchema]
