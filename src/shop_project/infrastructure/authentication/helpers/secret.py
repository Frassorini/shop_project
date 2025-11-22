from pydantic import BaseModel

from shop_project.infrastructure.authentication.helpers.auth_type import AuthType


class Secret(BaseModel):
    auth_type: AuthType
    payload: str
