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


@pytest.mark.parametrize(
    'input,expected',
    (
        ('0x0000000000000000000000000000000000000000000000000000000000000001', True),
        ('0x0000000000000000000000000000000000000000000000000000000000000000', False),
    )
)
def test_decode_bool(input, expected):
    output = decode_single('bool', input)
    assert output == expected


@pytest.mark.parametrize(
    'input,expected',
    (
        ('0x7465737400000000000000000000000000000000000000000000000000000000', 'test'),
        (
            '0x6162636465666768696a6b6c6d6e6f707172737475767778797a000000000000',
            'abcdefghijklmnopqrstuvwxyz',
        ),
        (
            '0x3031323334353637383921402324255e262a2829000000000000000000000000',
            '0123456789!@#$%^&*()',
        ),
    )
)
def test_decode_bytes32(input, expected):
    output = decode_single('bytes32', input)
    assert output == expected
