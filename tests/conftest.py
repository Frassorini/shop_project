pytest_plugins = [
    "tests.fixtures.infrastructure.uow",
    "tests.fixtures.infrastructure.database",
    "tests.fixtures.infrastructure.repository",
    
    "tests.fixtures.shared.unique_id",
    
    "tests.fixtures.domain.store_item",
    "tests.fixtures.domain.customer",
    "tests.fixtures.domain.cart",
    "tests.fixtures.domain.customer_order",
    "tests.fixtures.domain.supplier_order",
    "tests.fixtures.domain.domain_object",
]
