from typing import Sequence, Type
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
from shop_project.application.shared.scenarios.subject import (
    ensure_subject_type_or_raise_forbidden,
)
from shop_project.domain.entities.employee import Employee
from shop_project.domain.interfaces.subject import SubjectEnum


class EmployeeManagerReadService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type

    async def get_by_ids(
        self,
        access_payload: AccessTokenPayload,
        ids: list[UUID],
    ) -> list[EmployeeSchema]:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(Employee)
            .from_id(ids)
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resources()
            employees: Sequence[Employee] = resources.get_all(Employee)

        return [
            EmployeeSchema.model_validate(to_dto(employee)) for employee in employees
        ]

    async def get(
        self, access_payload: AccessTokenPayload, limit: int, offset: int
    ) -> list[EmployeeSchema]:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(Employee)
            .order_by("entity_id", desc=False)
            .offset(offset)
            .limit(limit)
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resources()
            employees: Sequence[Employee] = resources.get_all(Employee)

        return [
            EmployeeSchema.model_validate(to_dto(employee)) for employee in employees
        ]
