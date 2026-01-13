from dishka import Provider, Scope, provide

from shop_project.application.shared.policies.refund_initiation_policy import (
    RefundInitiationPolicy,
)
from shop_project.infrastructure.env_loader import get_env


class PolicyProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def refund_initiation_policy(
        self,
    ) -> RefundInitiationPolicy:
        return RefundInitiationPolicy(
            start_immediately=get_env("REFUND_INITIATION_POLICY_START_IMMEDIATELY")
            == "true"
        )
