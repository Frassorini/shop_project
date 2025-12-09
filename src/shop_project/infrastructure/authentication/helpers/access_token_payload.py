from uuid import UUID

from pydantic import BaseModel

from shop_project.domain.interfaces.subject import SubjectEnum


class AccessTokenPayload(BaseModel):
    subject_type: SubjectEnum
    account_id: UUID
