from pydantic import BaseModel, SecretStr

from shop_project.infrastructure.entities.secret import AuthType


class Credential(BaseModel):
    auth_type: AuthType
    payload: dict[str, SecretStr]
