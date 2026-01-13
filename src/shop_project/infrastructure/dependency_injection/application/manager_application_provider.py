from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.manager.commands.background_manager_service import (
    BackgroundManagerService,
)
from shop_project.application.manager.commands.employee_manager_service import (
    EmployeeManagerService,
)
from shop_project.application.manager.commands.product_manager_service import (
    ProductManagerService,
)
from shop_project.application.manager.commands.shipment_manager_service import (
    ShipmentManagerService,
)
from shop_project.application.manager.queries.employee_manager_read_service import (
    EmployeeManagerReadService,
)
from shop_project.application.manager.queries.operation_log_read_service import (
    OperationLogReadService,
)
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_task_sender import ITaskSender
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.domain.services.shipment_activation_service import (
    ShipmentActivationService,
)
from shop_project.domain.services.shipment_cancel_service import ShipmentCancelService
from shop_project.domain.services.shipment_receive_service import ShipmentReceiveService


class ManagerApplicationProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def product_manager_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> ProductManagerService:
        return ProductManagerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def shipment_manager_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        shipment_activation_service: ShipmentActivationService,
        shipment_cancel_service: ShipmentCancelService,
        shipment_receive_service: ShipmentReceiveService,
    ) -> ShipmentManagerService:
        return ShipmentManagerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            shipment_activation_service=shipment_activation_service,
            shipment_cancel_service=shipment_cancel_service,
            shipment_receive_service=shipment_receive_service,
        )

    @provide
    async def operation_log_read_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> OperationLogReadService:
        return OperationLogReadService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def employee_manager_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> EmployeeManagerService:
        return EmployeeManagerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def employee_manager_read_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> EmployeeManagerReadService:
        return EmployeeManagerReadService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
        )

    @provide
    async def background_manager_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        task_sender_service: ITaskSender,
    ) -> BackgroundManagerService:
        return BackgroundManagerService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            task_sender_service=task_sender_service,
        )
