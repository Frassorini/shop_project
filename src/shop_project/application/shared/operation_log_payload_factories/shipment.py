from shop_project.application.entities.operation_log.operation_log_payload_implementations.shipment import (
    ActivateShipmentItem,
    ActivateShipmentOperationLogPayload,
    CancelShipmentOperationLogPayload,
    ReceiveShipmentOperationLogPayload,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.shipment_dto import ShipmentDTO


def create_activate_shipment_payload(
    access_token_payload: AccessTokenPayload,
    shipment_dto: ShipmentDTO,
) -> ActivateShipmentOperationLogPayload:
    return ActivateShipmentOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        shipment_id=shipment_dto.entity_id,
        items=[
            ActivateShipmentItem(
                product_id=item.product_id,
                amount=item.amount,
            )
            for item in shipment_dto.items
        ],
    )


def create_cancel_shipment_payload(
    access_token_payload: AccessTokenPayload,
    shipment_dto: ShipmentDTO,
) -> CancelShipmentOperationLogPayload:
    return CancelShipmentOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        shipment_id=shipment_dto.entity_id,
    )


def create_receive_shipment_payload(
    access_token_payload: AccessTokenPayload,
    shipment_dto: ShipmentDTO,
) -> ReceiveShipmentOperationLogPayload:
    return ReceiveShipmentOperationLogPayload(
        subject_type=access_token_payload.subject_type,
        subject_id=access_token_payload.account_id,
        shipment_id=shipment_dto.entity_id,
    )
