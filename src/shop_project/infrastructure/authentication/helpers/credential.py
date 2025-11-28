from pydantic import BaseModel, SecretStr

from shop_project.infrastructure.authentication.helpers.auth_type import AuthType


class Credential(BaseModel):
    auth_type: AuthType
    payload: dict[str, SecretStr]
