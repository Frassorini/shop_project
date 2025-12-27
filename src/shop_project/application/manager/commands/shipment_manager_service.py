from typing import Type
from uuid import UUID

from shop_project.application.manager.schemas.shipment_schema import (
    CreateShipmentSchema,
    ShipmentSchema,
    ShipmentSummarySchema,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.dto.mapper import to_dto
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.scenarios.entity import (
    get_one_or_raise_forbidden,
    get_one_or_raise_not_found,
)
from shop_project.application.shared.scenarios.subject import (
    ensure_subject_type_or_raise_forbidden,
)
from shop_project.domain.entities.manager import Manager
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import ShipmentSummary
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.interfaces.subject import SubjectEnum
from shop_project.domain.services.shipment_activation_service import (
    ShipmentActivationService,
    ShipmentRequest,
)
from shop_project.domain.services.shipment_cancel_service import ShipmentCancelService
from shop_project.domain.services.shipment_receive_service import ShipmentReceiveService


class ShipmentManagerService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        shipment_activation_service: ShipmentActivationService,
        shipment_cancel_service: ShipmentCancelService,
        shipment_receive_service: ShipmentReceiveService,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._shipment_activation_service: ShipmentActivationService = (
            shipment_activation_service
        )
        self._shipment_cancel_service: ShipmentCancelService = shipment_cancel_service
        self._shipment_receive_service: ShipmentReceiveService = (
            shipment_receive_service
        )

    async def create_shipment(
        self,
        access_payload: AccessTokenPayload,
        create_shipment_schema: CreateShipmentSchema,
    ) -> ShipmentSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .load(Product)
            .from_id([item.product_id for item in create_shipment_schema.items])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )
            products = resources.get_all(Product)

            inventory = ProductInventory(products)
            shipment_request = ShipmentRequest()
            for item in create_shipment_schema.items:
                shipment_request.add_item(item.product_id, item.amount)

            shipment = self._shipment_activation_service.activate(
                inventory, shipment_request
            )

            resources.put(Shipment, shipment)

            uow.mark_commit()

        return ShipmentSchema.model_validate(to_dto(shipment))

    async def cancel_shipment(
        self, access_payload: AccessTokenPayload, shipment_id: UUID
    ) -> ShipmentSummarySchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .load(Shipment)
            .from_id([shipment_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )
            shipment = get_one_or_raise_not_found(resources, Shipment, shipment_id)

            summary = self._shipment_cancel_service.cancel(shipment)

            resources.put(ShipmentSummary, summary)
            resources.delete(Shipment, shipment)

            uow.mark_commit()

        return ShipmentSummarySchema.model_validate(to_dto(summary))

    async def receive_shipment(
        self, access_payload: AccessTokenPayload, shipment_id: UUID
    ) -> ShipmentSummarySchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .load(Shipment)
            .from_id([shipment_id])
            .for_update()
            .load(Product)
            .from_previous()
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )
            shipment = get_one_or_raise_not_found(resources, Shipment, shipment_id)
            products = resources.get_all(Product)

            inventory = ProductInventory(products)
            summary = self._shipment_receive_service.receive(inventory, shipment)

            resources.put(ShipmentSummary, summary)
            resources.delete(Shipment, shipment)

            uow.mark_commit()

        return ShipmentSummarySchema.model_validate(to_dto(summary))
