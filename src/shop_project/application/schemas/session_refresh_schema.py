from pydantic import BaseModel, SecretStr


class SessionRefreshSchema(BaseModel):
    refresh_token: SecretStr
    access_token: SecretStr
