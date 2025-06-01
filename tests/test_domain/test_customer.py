from domain.customer import Customer


def test_create_customer() -> None:
    customer = Customer(name='Andrew')
    assert customer.name == 'Andrew'