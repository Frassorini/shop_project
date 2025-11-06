from dependency_injector.providers import Resource
from unittest.mock import MagicMock, patch

from dependency_injector import containers, providers
from contextlib import contextmanager
from typing import Generator

import pytest

class ResourceNotInitialized(Exception):
    pass

class MyTestResource:
    def __init__(self, value: int) -> None:
        self.value = value
        self.is_initialized = False
    
    def init(self) -> None:
        # print("init resource")
        self.is_initialized = True

    def show(self) -> None:
        if self.is_initialized:
            print(self.value)
        else:
            raise ResourceNotInitialized("Resource is not initialized")

    def dispose(self) -> None:
        # print("dispose resource")
        self.is_initialized = False

# Контекстный менеджер для Resource
@contextmanager
def my_test_resource(value: int) -> Generator[MyTestResource, None, None]:
    resource = MyTestResource(value)
    resource.init()  # автоматически инициализируем
    try:
        yield resource
    finally:
        resource.dispose()  # автоматически очищаем

# Контейнер с Resource
class MyTestContainer(containers.DeclarativeContainer):
    resource = providers.Resource(
        my_test_resource,
        value=42
    )


def test_resource() -> None:
    with my_test_resource(42) as res:
        assert res.value == 42
        assert res.is_initialized
    
    assert not res.is_initialized


def test_resource_not_entered() -> None:
    resource = MyTestResource(42)
    assert not resource.is_initialized
    
    with pytest.raises(ResourceNotInitialized):
        resource.show()

def test_container_resource_lifecycle() -> None:
    container = MyTestContainer()

    # Инициализация ресурсов через контейнер
    
    # print("init resources in test")
    
    assert not container.resource.initialized
    
    container.init_resources()

    assert container.resource.initialized
    
    # Получаем реальный объект через 'with' (контейнер сам вызывает __enter__)
    resource: MyTestResource = container.resource() # type: ignore
    
    # print(resource)
    
    # print("override")
    
    spy_cm = MagicMock(wraps=my_test_resource)
    
    container.resource.override( # type: ignore
        providers.Resource(spy_cm, value=10)
    )
    # print("overrode")
    assert resource.is_initialized
    assert container.resource.initialized # Пишет инициализирован, но это не правда
    assert not spy_cm.called
    assert not resource is container.resource
    
    resource2: MyTestResource = container.resource() # type: ignore 
    assert container.resource.initialized
    assert resource2.value == 10
    assert spy_cm.called

    # После выхода из блока ресурс уже disposed
    container.shutdown_resources()

    assert not resource.is_initialized
    assert not resource2.is_initialized



def test_container_resource_lifecycle2() -> None:
    container = MyTestContainer()

    spy_cm = MagicMock(wraps=my_test_resource)

    container.resource.override( # type: ignore
        providers.Resource(spy_cm, value=10)
    )

    container.shutdown_resources()

    assert not container.resource.initialized
    assert not spy_cm.called

