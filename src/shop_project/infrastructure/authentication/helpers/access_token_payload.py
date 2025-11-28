from uuid import UUID

from pydantic import BaseModel

from shop_project.infrastructure.entities.account import SubjectType


class AccessTokenPayload(BaseModel):
    subject_type: SubjectType
    account_id: UUID
