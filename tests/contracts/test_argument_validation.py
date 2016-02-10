import pytest

from populus.contracts.functions import validate_argument


@pytest.mark.parametrize(
    "_type,value,expected",
    (
        # Uint
        ("uint256", 0, True),
        ("uint256", 1, True),
        ("uint256", -1, False),
        ("uint256", 2 ** 256 - 1, True),
        ("uint256", 2 ** 256, False),
        # Int
        ("int256", 0, True),
        ("int256", 1, True),
        ("int256", -1, True),
        ("int256", 2 ** 256 / 2 - 1, True),
        ("int256", 2 ** 256 / 2, False),
        # bytes32
        ("bytes32", "", True),
        ("bytes32", "1", True),
        ("bytes32", "1" * 32, True),
        ("bytes32", "1" * 33, False),
        # address
        ("address", "0x0000000000000000000000000000000000000000", True),
        ("address", "0000000000000000000000000000000000000000", True),
        ("address", "000000000000000000000000000000000000000", False),
        ("address", "0x000000000000000000000000000000000000000", False),
        # string
        ("string", "", True),
        ("string", "0" * 200, True),
        # bytes
        ("bytes", "", True),
        ("bytes", "0" * 200, True),
        # arrays fixed
        ("uint256[3]", [0, 1, 2], True),
        ("uint256[3]", ['0', '1', '2'], False),
        ("uint256[3]", [0, 1, '2'], False),
        ("uint256[2]", [0, 1, 2], False),
        ("uint256[4]", [0, 1, 2], False),
        # arrays unsized
        ("uint256[]", [0, 1, 2], True),
        ("uint256[]", [0, 1], True),
        # arrays nested
        ("uint256[2][3]", [[1, 2], [3, 4], [5, 6]], True),
        ("uint256[2][3]", [[1, 2, 3], [4, 5, 6]], False),
        ("uint256[][2]", [[1, 2, 3, 4, 5], [3, 4]], True),
        ("uint256[][2]", [[1, 2], [3, 4], [5, 6], [7, 8]], False),
        ("uint256[2][]", [[1, 2],], True),
        ("uint256[2][]", [[1, 2], [3, 4], [5, 6]], True),
        # arrays nested
        ("uint256[1][3][2]", [[[1], [2], [3]], [[4], [5], [6]]], True),
    )
)
def test_function_argument_validation(_type, value, expected):
    actual = validate_argument(_type, value)
    assert actual == expected
