from shop_project.application.schemas.base_schema import BaseSchema


class ClaimTokenSchema(BaseSchema):
    claim_token: str
