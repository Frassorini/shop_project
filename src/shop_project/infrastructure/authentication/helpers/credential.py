from dataclasses import dataclass
from typing import Any

from shop_project.infrastructure.authentication.helpers.auth_type import AuthType


@dataclass(frozen=True)
class Credential:
    auth_type: AuthType
    payload: dict[str, Any]
