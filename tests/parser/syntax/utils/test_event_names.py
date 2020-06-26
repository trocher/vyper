import pytest
from pytest import raises

from vyper import compiler
from vyper.exceptions import (
    EventDeclarationException,
    NamespaceCollision,
    UnknownType,
)

fail_list = [  # noqa: E122
    """
event Âssign:
    variable: int128

@public
def foo(i: int128) -> int128:
    temp_var : int128 = i
    log Âssign(temp_var)
    return temp_var
    """,
    (
        """
event int128:
    variable: int128

@public
def foo(i: int128) -> int128:
    temp_var : int128 = i
    log int128(temp_var)
    return temp_var
    """,
        NamespaceCollision,
    ),
    (
        """
event decimal:
    variable: int128

@public
def foo(i: int128) -> int128:
    temp_var : int128 = i
    log decimal(temp_var)
    return temp_var
    """,
        NamespaceCollision,
    ),
    """
event wei:
    variable: int128

@public
def foo(i: int128) -> int128:
    temp_var : int128 = i
    log wei(temp_var)
    return temp_var
    """,
    """
event false:
    variable: int128

@public
def foo(i: int128) -> int128:
    temp_var : int128 = i
    log false(temp_var)
    return temp_var
    """,
    (
        """
Transfer: eve.t({_from: indexed(address)})
    """,
        UnknownType,
    ),
    (
        """
event Transfer:
    _from: i.dexed(address)
    _to: indexed(address)
    lue: uint256
    """,
        UnknownType,
    ),
]


@pytest.mark.parametrize("bad_code", fail_list)
def test_varname_validity_fail(bad_code):
    if isinstance(bad_code, tuple):
        with raises(bad_code[1]):
            compiler.compile_code(bad_code[0])
    else:
        with raises(EventDeclarationException):
            compiler.compile_code(bad_code)


valid_list = [
    """
event Assigned:
    variable: int128

@public
def foo(i: int128) -> int128:
    variable : int128 = i
    log Assigned(variable)
    return variable
    """,
    """
event _Assign:
    variable: int128

@public
def foo(i: int128) -> int128:
    variable : int128 = i
    log _Assign(variable)
    return variable
    """,
    """
event Assigned1:
    variable: int128

@public
def foo(i: int128) -> int128:
    variable : int128 = i
    log Assigned1(variable)
    return variable
    """,
]


@pytest.mark.parametrize("good_code", valid_list)
def test_varname_validity_success(good_code):
    assert compiler.compile_code(good_code) is not None
