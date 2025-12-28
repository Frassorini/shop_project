from shop_project.application.entities.operation_log.operation_log_payload_implementations.product import (
    CreateProductOperationLogPayload,
    DeleteProductOperationLogPayload,
    UpdateProductOperationLogPayload,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.product_dto import ProductDTO


def create_create_product_payload(
    access_token_payload: AccessTokenPayload, product_dto: ProductDTO
) -> CreateProductOperationLogPayload:
    return CreateProductOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        product_name=product_dto.name,
        product_id=product_dto.entity_id,
        product_price=product_dto.price,
    )


def create_update_product_payload(
    access_token_payload: AccessTokenPayload, product_dto: ProductDTO
) -> UpdateProductOperationLogPayload:
    return UpdateProductOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        product_name=product_dto.name,
        product_id=product_dto.entity_id,
        product_price=product_dto.price,
    )


def create_delete_product_payload(
    access_token_payload: AccessTokenPayload, product_dto: ProductDTO
) -> DeleteProductOperationLogPayload:
    return DeleteProductOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        product_id=product_dto.entity_id,
    )
