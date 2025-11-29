import pytest
from plum import NotFoundLookupError, dispatch, overload


@overload
def func_args(val: str) -> str:
    return "str"


@overload
def func_args(val: int) -> str:
    return "int"


@dispatch
def func_args(val: int | str) -> str: ...


@overload
def func_kwargs(*, val: str) -> str:
    return "str1"


@overload
def func_kwargs(*, val: int) -> str:
    return "int"


@dispatch
def func_kwargs(*, val: int | str) -> str: ...


def test_plum() -> None:
    assert func_args(1) == "int"
    assert func_args("1") == "str"

    with pytest.raises(NotFoundLookupError):
        func_args(val=1)
        func_args(val="1")

    # docs: "Keyword arguments are certainly supported, but they are not used in the decision making for which method to call"
    assert func_kwargs(val=1) == "int"
    assert func_kwargs(val="whatever") == "int"
