import pytest

from populus.utils.packaging import (
    construct_dependency_identifier,
)


@pytest.mark.parametrize(
    'fn_args,expected',
    (
        (("owned", "owned==1.0.0", "ipfs://Qm.."), "1.0.0"),
        (("owned", "owned>=1.0.0", "ipfs://Qm.."), ">=1.0.0"),
        (("owned", "ipfs://Qm..", "ipfs://Qm.."), "ipfs://Qm.."),
        # aliased
        (("powned", "owned==1.0.0", "ipfs://Qm.."), "owned==1.0.0"),
        (("powned", "owned>=1.0.0", "ipfs://Qm.."), "owned>=1.0.0"),
    )
)
def test_construct_dependency_identifier(fn_args, expected):
    actual = construct_dependency_identifier(*fn_args)
    assert actual == expected
