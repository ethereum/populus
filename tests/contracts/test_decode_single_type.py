import pytest

from populus.contracts.utils import decode_single


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
        (
            '0x6162630000000000616263000000000000000000000000000000000000000000',
            'abc\x00\x00\x00\x00\x00abc',
        ),
    )
)
def test_decode_bytes32(input, expected):
    output = decode_single('bytes32', input)
    assert output == expected


def test_decode_bytes():
    input = '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000024b0f07e44616263646162636461626364616263646162636461626364616263646162636400000000000000000000000000000000000000000000000000000000'
    output = decode_single('bytes', input)
    assert output == '\xb0\xf0~Dabcdabcdabcdabcdabcdabcdabcdabcd'



@pytest.mark.parametrize(
    'input,expected',
    (
        (
            '0x0000000000000000000000000000000000000000000000000000000000000000',
            '0x0000000000000000000000000000000000000000',
        ),
        (
            '0x000000000000000000000000c305c901078781c232a2a521c2af7980f8385ee9',
            '0xc305c901078781c232a2a521c2af7980f8385ee9',
        ),
        (
            '0x0000000000000000000000000005c901078781c232a2a521c2af7980f8385ee9',
            '0x0005c901078781c232a2a521c2af7980f8385ee9',
        ),
        (
            '0x000000000000000000000000c305c901078781c232a2a521c2af7980f8385000',
            '0xc305c901078781c232a2a521c2af7980f8385000',
        ),
        (
            '0x0000000000000000000000000005c901078781c232a2a521c2af7980f8385000',
            '0x0005c901078781c232a2a521c2af7980f8385000',
        ),
    )
)
def test_decode_address(input, expected):
    output = decode_single('address', input)
    assert output == expected


@pytest.mark.parametrize('_type', ('address', 'bytes32', 'uint256', 'int256', 'bool'))
def test_raises_on_empty_data(_type):
    with pytest.raises(AssertionError):
        decode_single(_type, '0x')
