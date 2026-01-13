from typing import Type

from shop_project.application.background.base_task_handler import NullTaskParams
from shop_project.application.background.implementations.purchase_flow_handler import (
    BatchFinalizeNotPaidTasksHandler,
    BatchPaidReservationTimeOutTaskHandler,
    BatchWaitPaymentTaskHandler,
    BatchWaitRefundTaskHandler,
)
from shop_project.application.entities.task import Task, create_task
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_task_sender import ITaskSender
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.shared.operation_log_payload_factories.background import (
    create_manual_redeliver_tasks_payload,
    create_manual_trigger_purchase_flow_payload,
)
from shop_project.application.shared.scenarios.entity import (
    get_one_or_raise_forbidden,
)
from shop_project.application.shared.scenarios.operation_log import log_operation
from shop_project.application.shared.scenarios.subject import (
    ensure_subject_type_or_raise_forbidden,
)
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import SubjectEnum


class BackgroundManagerService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        task_sender_service: ITaskSender,
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type
        self._task_sender_service: ITaskSender = task_sender_service

    async def trigger_purchase_flow(self, access_payload: AccessTokenPayload) -> None:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )

            tasks = [
                create_task(BatchWaitPaymentTaskHandler, NullTaskParams()),
                create_task(BatchWaitRefundTaskHandler, NullTaskParams()),
                create_task(BatchPaidReservationTimeOutTaskHandler, NullTaskParams()),
                create_task(BatchFinalizeNotPaidTasksHandler, NullTaskParams()),
            ]

            for task in tasks:
                resources.put(Task, task)

            operation_log = create_manual_trigger_purchase_flow_payload(
                access_payload,
            )
            log_operation(resources, operation_log)

            uow.mark_commit()

    async def manual_redeliver_tasks(self, access_payload: AccessTokenPayload) -> None:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)
        TASKS_PER_ITERATION = 100

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )

            operation_log = create_manual_redeliver_tasks_payload(
                access_payload,
            )
            log_operation(resources, operation_log)

            uow.mark_commit()

        check_more_tasks_flag = True
        already_checked_tasks = 0

        while check_more_tasks_flag:
            async with self._unit_of_work_factory.create(
                self._query_builder_type(mutating=True)
                .load(Manager)
                .from_id([access_payload.account_id])
                .no_lock()
                .load(Task)
                .order_by("entity_id", desc=False)
                .limit(TASKS_PER_ITERATION)
                .offset(already_checked_tasks)
                .no_lock()
                .build()
            ) as uow:
                resources = uow.get_resources()
                manager = get_one_or_raise_forbidden(
                    resources, Manager, access_payload.account_id
                )

                tasks = [task for task in resources.get_all(Task)]

                if len(tasks) < TASKS_PER_ITERATION:
                    check_more_tasks_flag = False

                for task in tasks:
                    await self._task_sender_service.send(task)

                already_checked_tasks += len(tasks)
