from typing import Type
from uuid import UUID

from shop_project.application.manager.schemas.employee_schema import EmployeeSchema
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
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import SubjectEnum


class EmployeeManagerService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type

    async def authorize_employee(
        self, access_payload: AccessTokenPayload, employee_id: UUID
    ) -> EmployeeSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .load(Employee)
            .from_id([employee_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )
            employee = get_one_or_raise_not_found(resources, Employee, employee_id)

            employee.authorize()

            uow.mark_commit()

        return EmployeeSchema.model_validate(to_dto(employee))

    async def unauthorize_employee(
        self, access_payload: AccessTokenPayload, employee_id: UUID
    ) -> EmployeeSchema:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(Manager)
            .from_id([access_payload.account_id])
            .for_share()
            .load(Employee)
            .from_id([employee_id])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resources()
            manager = get_one_or_raise_forbidden(
                resources, Manager, access_payload.account_id
            )
            employee = get_one_or_raise_not_found(resources, Employee, employee_id)

            employee.unauthorize()

            uow.mark_commit()

        return EmployeeSchema.model_validate(to_dto(employee))
