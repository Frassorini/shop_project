from abc import ABC

from pydantic import BaseModel


class NotificationMessage(BaseModel, ABC): ...
