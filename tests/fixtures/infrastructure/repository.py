# @pytest.fixture
# def inmem_customer_repository_factory(
#     test_db_in_memory: Database,
# ) -> Callable[[list[Customer]], Coroutine[None, None, BaseRepository[Customer]]]:
#     async def factory(customers: list[Customer]) -> BaseRepository[Customer]:
#         session = test_db_in_memory.create_session()
#         repository = CustomerRepository(session)
#         await repository.create(customers)
#         return repository

#     return factory
