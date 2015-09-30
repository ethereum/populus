import pytest

from populus.contracts import (
    Function,
    FunctionGroup,
)
from populus.contracts.functions import (
    validate_argument,
)

int8_a = {'type': 'int8', 'name': 'a'}
int8_b = {'type': 'int8', 'name': 'b'}
uint8_a = {'type': 'uint8', 'name': 'a'}
uint8_b = {'type': 'uint8', 'name': 'b'}
int256_a = {'type': 'int256', 'name': 'a'}
int256_b = {'type': 'int256', 'name': 'b'}
uint256_a = {'type': 'uint256', 'name': 'a'}
uint256_b = {'type': 'uint256', 'name': 'b'}
bytes8_x = {'type': 'bytes8', 'name': 'x'}
bytes8_y = {'type': 'bytes8', 'name': 'y'}
bytes32_x = {'type': 'bytes32', 'name': 'x'}
bytes32_y = {'type': 'bytes32', 'name': 'y'}
address_m = {'type': 'address', 'name': 'm'}
address_n = {'type': 'address', 'name': 'n'}


@pytest.mark.parametrize(
    "val,arg_info,expected",
    (
        # int8
        (0, int8_a, True),
        (100, int8_a, True),
        (127, int8_a, True),
        (128, int8_a, False),
        (-100, int8_a, True),
        (-127, int8_a, True),
        (-128, int8_a, False),
        ('a', int8_a, False),
        ('arst', int8_a, False),
        ('\x00\x00', int8_a, False),
        # uint8
        (0, uint8_a, True),
        (100, uint8_a, True),
        (255, uint8_a, True),
        (256, uint8_a, False),
        (-1, uint8_a, False),
        (-100, uint8_a, False),
        ('a', uint8_a, False),
        ('arst', uint8_a, False),
        ('\x00\x00', uint8_a, False),
        # int256
        (0, int256_a, True),
        (100, int256_a, True),
        (-100, int256_a, True),
        ('a', int256_a, False),
        ('arst', int256_a, False),
        ('\x00\x00', int256_a, False),
        # uint256
        (0, uint256_a, True),
        (100, uint256_a, True),
        (-100, uint256_a, False),
        ('a', uint256_a, False),
        ('arst', uint256_a, False),
        ('\x00\x00', uint256_a, False),
        # bytes8
        ('', bytes8_x, True),
        ('a', bytes8_x, True),
        ('abcdefgh', bytes8_x, True),
        ('12345678', bytes8_x, True),
        ('123456789', bytes8_x, False),
        ('abcdefghi', bytes8_x, False),
        # bytes32
        ('', bytes32_x, True),
        ('a', bytes32_x, True),
        ('abcdefgh', bytes32_x, True),
        ('12345678', bytes32_x, True),
        ('123456789', bytes32_x, True),
        ('abcdefghi', bytes32_x, True),
        ('12345678901234567890123456789012', bytes32_x, True),
        ('123456789012345678901234567890123', bytes32_x, False),
        # address
        ('0x0000000000000000000000000000000000000000', address_m, True),
        ('0x0a00c0300800004004009cdfe100000000000000', address_m, True),
        ('0x0a00c0300800004004009cdfe1000000000000000', address_m, False),
        ('0x0a00c0300800004004009cdfe10000000000000', address_m, False),
        ('0000000000000000000000000000000000000000', address_m, True),
        ('0a00c0300800004004009cdfe100000000000000', address_m, True),
        ('0a00c0300800004004009cdfe1000000000000000', address_m, False),
        ('0a00c0300800004004009cdfe10000000000000', address_m, False),
    )
)
def test_argument_matching(val, arg_info, expected):
    assert validate_argument(arg_info, val) is expected


int8_a = {'type': 'int8', 'name': 'a'}
int8_b = {'type': 'int8', 'name': 'b'}
uint8_a = {'type': 'uint8', 'name': 'a'}
uint8_b = {'type': 'uint8', 'name': 'b'}
int256_a = {'type': 'int256', 'name': 'a'}
int256_b = {'type': 'int256', 'name': 'b'}
uint256_a = {'type': 'uint256', 'name': 'a'}
uint256_b = {'type': 'uint256', 'name': 'b'}
bytes8_x = {'type': 'bytes8', 'name': 'x'}
bytes8_y = {'type': 'bytes8', 'name': 'y'}
bytes32_x = {'type': 'bytes32', 'name': 'x'}
bytes32_y = {'type': 'bytes32', 'name': 'y'}
address_m = {'type': 'address', 'name': 'm'}
address_n = {'type': 'address', 'name': 'n'}


f_1a = Function('doit', [int8_a, uint8_a, int256_a, uint256_a])
f_1b = Function('doit', [int8_a, uint8_a, int8_b, int8_b])


f_group_1 = FunctionGroup([f_1a, f_1b])


def test_matching_with_similar_integers():
    assert f_group_1.get_function_for_call_signature((1, 2, 500, 500)) == f_1a
    with pytest.raises(TypeError):
        assert f_group_1.get_function_for_call_signature((1, 2, 100, 100))
    assert f_group_1.get_function_for_call_signature((1, 2, 100, -100)) == f_1b


f_2a = Function('doit', [uint256_a, bytes32_x, address_m])
f_2b = Function('doit', [uint256_a, address_n, bytes8_x])


f_group_2 = FunctionGroup([f_2a, f_2b])


def test_address_and_bytes_matching():
    assert f_group_2.get_function_for_call_signature((12345, 'arstarst', '0xd3cda913deb6f67967b99d67acdfa1712c293601')) == f_2a
    assert f_group_2.get_function_for_call_signature((12345, 'd3cda913deb6f67967b99d67acdfa1712c293601', '0xd3cda')) == f_2b
