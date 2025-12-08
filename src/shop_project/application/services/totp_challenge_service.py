from typing import Type

from shop_project.application.interfaces.interface_query_builder import IQueryBuilder
from shop_project.application.interfaces.interface_totp_service import ITotpService
from shop_project.application.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)
from shop_project.application.schemas.totp_request_schema import (
    EmailTotpRequestSchema,
    SmsTotpRequestSchema,
)
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp
from shop_project.infrastructure.exceptions import ResourcesException


class TotpChallengeService:
    def __init__(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        totp_service: ITotpService,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._query_builder_type = query_builder_type
        self._totp_service = totp_service

    async def begin_sms_challenge(self, totp_request: SmsTotpRequestSchema) -> None:
        totp_pair = self._totp_service.create_sms_code_message_pair(
            phone_number=totp_request.identifier
        )

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(ExternalIdTotp)
            .from_attribute("external_id", [totp_request.identifier])
            .and_()
            .from_attribute("external_id_type", ["phone"])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()

            try:
                totp_old = resources.get_one_by_attribute(
                    ExternalIdTotp, "external_id", totp_request.identifier
                )
            except ResourcesException:
                pass
            else:
                resources.delete(ExternalIdTotp, totp_old)

            resources.put(ExternalIdTotp, totp_pair.totp)

            uow.mark_commit()

        await self._totp_service.send_totp_message(totp_pair.message)

    async def begin_email_challenge(self, totp_request: EmailTotpRequestSchema) -> None:
        totp_pair = self._totp_service.create_email_code_message_pair(
            email=totp_request.identifier
        )

        async with self._unit_of_work_factory.create(
            self._query_builder_type(mutating=True)
            .load(ExternalIdTotp)
            .from_attribute("external_id", [totp_request.identifier])
            .and_()
            .from_attribute("external_id_type", ["email"])
            .for_update()
            .build()
        ) as uow:
            resources = uow.get_resorces()

            try:
                totp_old = resources.get_one_by_attribute(
                    ExternalIdTotp, "external_id", totp_request.identifier
                )
            except ResourcesException:
                pass
            else:
                resources.delete(ExternalIdTotp, totp_old)

            resources.put(ExternalIdTotp, totp_pair.totp)

            uow.mark_commit()

        await self._totp_service.send_totp_message(totp_pair.message)
