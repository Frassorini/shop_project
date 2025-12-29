from typing import Sequence, Type

from shop_project.application.entities.operation_log.operation_log import OperationLog
from shop_project.application.manager.schemas.operation_log_schema import (
    OperationLogSchema,
)
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
from shop_project.domain.interfaces.subject import SubjectEnum


class OperationLogReadService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
    ) -> None:
        self._unit_of_work_factory: IUnitOfWorkFactory = unit_of_work_factory
        self._query_builder_type: Type[IQueryBuilder] = query_builder_type

    async def get_after_sequence(
        self, access_payload: AccessTokenPayload, sequence: int, limit: int
    ) -> list[OperationLogSchema]:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(OperationLog)
            .greater_than("seq", sequence)
            .no_lock()
            .order_by("seq")
            .limit(limit)
            .build()
        ) as uow:
            resources = uow.get_resources()
            sequences: Sequence[OperationLog] = resources.get_all(OperationLog)

        return [
            OperationLogSchema.model_validate(to_dto(sequence))
            for sequence in sequences
        ]

    async def get_before_sequence(
        self, access_payload: AccessTokenPayload, sequence: int, limit: int
    ) -> list[OperationLogSchema]:
        ensure_subject_type_or_raise_forbidden(access_payload, SubjectEnum.MANAGER)

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=False)
            .load(OperationLog)
            .less_than("seq", sequence)
            .order_by("seq", desc=True)
            .limit(limit)
            .no_lock()
            .build()
        ) as uow:
            resources = uow.get_resources()
            sequences: Sequence[OperationLog] = resources.get_all(OperationLog)

            sorted_sequences = sorted(
                sequences, key=lambda x: x.seq if x.seq is not None else float("+inf")
            )

        return [
            OperationLogSchema.model_validate(to_dto(sequence))
            for sequence in sequences
        ]
