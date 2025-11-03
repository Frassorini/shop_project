# shop_project/containers/domain_container.py
from dependency_injector import containers, providers
from shop_project.infrastructure.dependency_injection.domain import factories


class DomainContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["shop_project.infrastructure.dependency_injection.domain.factories"]
    )

    checkout_service = providers.Factory(factories.checkout_service_factory)
    
    purchase_summary_service = providers.Factory(factories.purchase_summary_service_factory)
    purchase_reservation_service = providers.Factory(factories.purchase_reservation_service_factory)
    purchase_activation_service = providers.Factory(factories.purchase_activation_service_factory)
    purchase_claim_service = providers.Factory(factories.purchase_claim_service_factory)
    purchase_return_service = providers.Factory(factories.purchase_return_service_factory)
    
    shipment_summary_service = providers.Factory(factories.shipment_summary_service_factory)
    shipment_activation_service = providers.Factory(factories.shipment_activation_service_factory)
    shipment_receive_service = providers.Factory(factories.shipment_receive_service_factory)
    shipment_cancel_service = providers.Factory(factories.shipment_cancel_service_factory)

