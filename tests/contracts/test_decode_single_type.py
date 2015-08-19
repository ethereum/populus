import pytest

from populus.contracts import decode_single


@pytest.mark.parametrize(
    'input,expected',
    (
        ('0x0000000000000000000000000000000000000000000000000000000000000015', 21),
        ('0x0000000000000000000000000000000000000000000000000000000000000001', 1),
        ('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', -1),
        ('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff9c', -100),
    )
)
def test_decode_int256(input, expected):
    output = decode_single('int256', input)
    assert output == expected


@pytest.mark.parametrize(
    'input,expected',
    (
        ('0x0000000000000000000000000000000000000000000000000000000000000015', 21),
        ('0x0000000000000000000000000000000000000000000000000000000000000001', 1),
        ('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 2 ** 256 - 1),
        ('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff9c', 2 ** 256 -100),
    )
)
def test_decode_uint256(input, expected):
    output = decode_single('uint256', input)
    assert output == expected
