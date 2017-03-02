import pytest

from populus.utils.contracts import (
    compare_bytecode,
)


@pytest.mark.parametrize(
    "left,right,expected",
    (
        ("0x", "0x", True),
        ("", "0x", True),
        ("0x", "", True),
        ("", "", True),
        ("0x1234567890abcdef", "0x1234567890abcdef", True),
        ("1234567890abcdef", "0x1234567890abcdef", True),
        ("0x1234567890abcdef", "1234567890abcdef", True),
        ("0x1234567890abcdef", "0x", False),
        # with swarm hash.
        (
            "0x6060604052346000575b5b5b60358060186000396000f30060606040525b60005600a165627a7a72305820ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0029",
            "0x6060604052346000575b5b5b60358060186000396000f30060606040525b60005600a165627a7a72305820eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee0029",
            True,
        ),
        # only swarm hash
        (
            "0xa165627a7a72305820ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0029",
            "0xa165627a7a72305820eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee0029",
            True,
        ),
        # bad embedded swarm hash (too few bytes in hash)"
        (
            "0x6060604052346000575b5b5b60358060186000396000f30060606040525b60005600a165627a7a72305820ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0029",
            "0x6060604052346000575b5b5b60358060186000396000f30060606040525b60005600a165627a7a72305820eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee0029",
            False,
        ),
        # bad embedded swarm hash (bad wrapping bytes)"
        (
            "0x6060604052346000575b5b5b60358060186000396000f30060606040525b60005600a165627a7a72305820ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff0028", # should end with 29
            "0x6060604052346000575b5b5b60358060186000396000f30060606040525b60005600a165627a7a72305820eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee0028", # should end with 29
            False,
        ),
    ),
)
def test_compare_bytecode(left, right, expected):
    actual = compare_bytecode(left, right)
    assert actual is expected
