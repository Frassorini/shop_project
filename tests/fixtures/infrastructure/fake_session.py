from typing import Any, Callable, List

import pytest


class FakeSession:
    def __init__(self):
        self._in_transaction = False
        self.added: List[Any] = []
        self.deleted: List[Any] = []
        self.committed = False
        self.rolled_back = False
        self._is_closed = False

    def begin(self) -> None:
        self._ensure_not_closed()
        if self._in_transaction:
            raise RuntimeError("Transaction already started")
        self._in_transaction = True

    def commit(self) -> None:
        self._ensure_not_closed()
        self._ensure_in_transaction()
        self.committed = True
        self._in_transaction = False

    def rollback(self) -> None:
        self._ensure_not_closed()
        self._ensure_in_transaction()
        self.rolled_back = True
        self._in_transaction = False

    def add(self, obj: Any) -> None:
        self._ensure_not_closed()
        self._ensure_in_transaction()
        self.added.append(obj)

    def delete(self, obj: Any) -> None:
        self._ensure_not_closed()
        self._ensure_in_transaction()
        self.deleted.append(obj)
        
    def close(self) -> None:
        if self._is_closed:
            raise RuntimeError("Transaction already closed")
        self._is_closed = False

    def _ensure_in_transaction(self) -> None:
        if not self._in_transaction:
            raise RuntimeError("Operation outside of transaction")
    
    def _ensure_not_closed(self) -> None:
        if self._is_closed:
            raise RuntimeError("Transaction already closed")


@pytest.fixture
def fake_session_factory() -> Callable[[], FakeSession]:
    def factory() -> FakeSession:
        return FakeSession()
    return factory