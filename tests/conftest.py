import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--real-db",
        action="store_true",
        default=False,
        help="Run tests using real database instead of in-memory DB",
    )
    parser.addoption(
        "--real-broker",
        action="store_true",
        default=False,
        help="Run tests using real broker instead of in-memory broker",
    )


pytest_plugins = [
    "tests.fixtures.application.login",
    "tests.fixtures.application.totp",
    "tests.fixtures.application.registration",
    "tests.fixtures.application.purchase_activation",
    "tests.fixtures.infrastructure.unit_of_work",
    "tests.fixtures.infrastructure.database",
    "tests.fixtures.infrastructure.broker",
    "tests.fixtures.infrastructure.repository",
    "tests.fixtures.infrastructure.dependency_injection",
    "tests.fixtures.infrastructure.task",
    "tests.fixtures.infrastructure.claim_token",
    "tests.fixtures.infrastructure.account",
    "tests.fixtures.infrastructure.auth_session",
    "tests.fixtures.infrastructure.external_id_totp",
    "tests.fixtures.shared.unique_id",
    "tests.fixtures.domain.manager",
    "tests.fixtures.domain.employee",
    "tests.fixtures.domain.product",
    "tests.fixtures.domain.customer",
    "tests.fixtures.domain.purchase_draft",
    "tests.fixtures.domain.purchase_active",
    "tests.fixtures.domain.shipment",
    "tests.fixtures.domain.domain_object",
]
