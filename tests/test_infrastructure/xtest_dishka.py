from dishka.container import Container


from dishka import Provider, Scope, provide, make_container # type: ignore
from shop_project.infrastructure.unit_of_work import UnitOfWork
import pytest


class ProviderA(Provider):
    @provide(scope=Scope.APP)
    def value_a(self) -> None:
        return None


class ProviderB(Provider):
    @provide(scope=Scope.APP)
    def value_b(self, value_b: str) -> int:
        return len(value_b)


@pytest.mark.asyncio
async def test_resource_lifecycle():
    container = make_container(ProviderB(), ProviderA())
    
    result: Container = container
    
    print(result)