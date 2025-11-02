import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--real-db", action="store_true", default=False,
        help="Run tests using real database instead of in-memory DB",
    )


pytest_plugins = [
    "tests.fixtures.infrastructure.uow",
    "tests.fixtures.infrastructure.database",
    "tests.fixtures.infrastructure.repository",
    "tests.fixtures.infrastructure.dependency_injection",
    
    "tests.fixtures.shared.unique_id",
    
    "tests.fixtures.domain.product",
    "tests.fixtures.domain.customer",
    "tests.fixtures.domain.purchase_draft",
    "tests.fixtures.domain.purchase_active",
    "tests.fixtures.domain.shipment",
    "tests.fixtures.domain.domain_object",
]
