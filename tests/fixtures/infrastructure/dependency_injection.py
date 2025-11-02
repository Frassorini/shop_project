import pytest
from shop_project.infrastructure.dependency_injection.domain.container import DomainContainer

@pytest.fixture
def domain_container() -> DomainContainer:
    container = DomainContainer()
    
    # Пример подмены зависимости на мок
    # container[CheckoutService] = lambda: Mock(spec=CheckoutService)
    
    return container