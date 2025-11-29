from uuid import UUID

from pydantic import BaseModel

from shop_project.domain.interfaces.subject import SubjectType


class AccessTokenPayload(BaseModel):
    subject_type: SubjectType
    account_id: UUID
