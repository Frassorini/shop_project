from typing import Sequence

from shop_project.application.shared.interfaces.interface_payment_gateway import (
    IPaymentGateway,
    PaymentState,
)
from shop_project.application.shared.interfaces.interface_resource_container import (
    IResourceContainer,
)
from shop_project.domain.entities.escrow_account import (
    EscrowAccount,
)


async def get_state_map(
    payment_gateway: IPaymentGateway, escrow_accounts: Sequence[EscrowAccount]
) -> dict[PaymentState, list[EscrowAccount]]:
    fetched_states = await payment_gateway.get_states(
        [str(escrow_account.entity_id) for escrow_account in escrow_accounts]
    )

    state_map: dict[PaymentState, list[EscrowAccount]] = {}
    for escrow_account in escrow_accounts:
        state = fetched_states[str(escrow_account.entity_id)]
        state_map.setdefault(state, []).append(escrow_account)

    return state_map


async def get_payment_state_map(
    resources: IResourceContainer, payment_gateway: IPaymentGateway
) -> dict[PaymentState, list[EscrowAccount]]:
    escrow_accounts = resources.get_all(EscrowAccount)
    state_map = await get_state_map(payment_gateway, escrow_accounts)
    return state_map
