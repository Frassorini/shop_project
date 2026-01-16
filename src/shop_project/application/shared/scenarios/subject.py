from shop_project.application.exceptions import ApplicationForbiddenError
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.domain.interfaces.subject import SubjectEnum


def ensure_subject_type_or_raise_forbidden(
    access_token: AccessTokenPayload, subject_type: SubjectEnum
) -> None:
    if access_token.subject_type != subject_type:
        raise ApplicationForbiddenError
