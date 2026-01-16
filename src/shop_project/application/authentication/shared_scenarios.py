from shop_project.application.entities.external_id_totp import ExternalIdTotp
from shop_project.application.exceptions import (
    ApplicationForbiddenError,
)
from shop_project.application.shared.interfaces.interface_resource_container import (
    IResourceContainer,
)
from shop_project.application.shared.interfaces.interface_totp_service import (
    ITotpService,
)


def verify_and_consume_totp(
    resources: IResourceContainer,
    totp_service: ITotpService,
    external_id: str,
    code: str,
) -> None:
    totp = resources.get_one_or_none_by_attribute(
        ExternalIdTotp, "external_id", external_id
    )
    if not totp:
        raise ApplicationForbiddenError
    if not totp_service.verify_totp(totp, code):
        raise ApplicationForbiddenError
    resources.delete(ExternalIdTotp, totp)
