from fastapi import Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel


class OAuth2RefreshTokenRequestForm:
    def __init__(
        self,
        grant_type: str = Form(pattern="^refresh_token$"),
        refresh_token: str = Form(...),
        scope: str = Form(""),
        client_id: str | None = Form(None),
        client_secret: str | None = Form(None),
    ):
        if grant_type != "refresh_token":
            raise ValueError("Invalid grant_type")
        self.refresh_token = refresh_token


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", refreshUrl="/refresh")
