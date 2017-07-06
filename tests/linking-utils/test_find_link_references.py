import pytest

from populus.utils.linking import find_link_references

CODE = "0x60606040526101af806100126000396000f3606060405260e060020a600035046330fd609b81146100475780637a8ebf591461008f578063a95f5076146100d7578063db81daaa1461011f578063e7f09e0514610167575b005b61004560e260020a6303155a6702606090815273__Has_Underscores_In_The_Name___________90630c55699c906064906000906004818660325a03f41561000257505050565b61004560e260020a6303155a6702606090815273___StartsWithUnderscore_________________90630c55699c906064906000906004818660325a03f41561000257505050565b61004560e260020a6303155a6702606090815273__LongerThan40Characters12345678901234__90630c55699c906064906000906004818660325a03f41561000257505050565b61004560e260020a6303155a6702606090815273__B1____________________________________90630c55699c906064906000906004818660325a03f41561000257505050565b61004560e260020a6303155a6702606090815273__A_____________________________________90630c55699c906064906000906004818660325a03f4156100025750505056"


FULL_NAMES = (
    'LongerThan40Characters1234567890123456789012345678901234567890',
    'B1',
    'A',
    '_StartsWithUnderscore',
    'Has_Underscores_In_The_Name',
    'Close',
    'Together',
    'Some32ByteValue',
    'MathLib',
    'NothingButLink',
)


@pytest.mark.parametrize(
    'bytecode,expected',
    (
        ('0x', tuple()),
        ('', tuple()),
        (
            '0x__NothingButLink________________________',
            (
                {
                    'name': 'NothingButLink',
                    'offset': 0,
                    'length': 40,
                },
            ),
        ),
        (
            '0xabcdef__MathLib_______________________________12345',
            (
                {
                    'name': 'MathLib',
                    'offset': 6,
                    'length': 40,
                },
            ),
        ),
        (
            '0xabcdef__Some32ByteValue_______________________12345',
            (
                {
                    'name': 'Some32ByteValue',
                    'offset': 6,
                    'length': 40,
                },
            )
        ),
        (
            '0xabcdef__Close___________________________________Together______________________________abcdef',
            (
                {
                    'name': 'Close',
                    'offset': 6,
                    'length': 40,
                },
                {
                    'name': 'Together',
                    'offset': 46,
                    'length': 40,
                },
            )
        ),
        (
            CODE,
            (
                {
                    'name': 'Has_Underscores_In_The_Name',
                    'offset': 220,
                    'length': 40,
                },
                {
                    'name': '_StartsWithUnderscore',
                    'offset': 364,
                    'length': 40,
                },
                {
                    'name': 'LongerThan40Characters1234567890123456789012345678901234567890',
                    'offset': 508,
                    'length': 40,
                },
                {
                    'name': 'B1',
                    'offset': 652,
                    'length': 40,
                },
                {
                    'name': 'A',
                    'offset': 796,
                    'length': 40,
                },
            )
        ),
    ),
)
def test_find_link_references(bytecode, expected):
    actual = find_link_references(bytecode, FULL_NAMES)

    assert len(actual) == len(expected)

    for left, right in zip(actual, expected):
        assert left.full_name == right['name']
        assert left.offset == right['offset']
        assert left.length == right['length']
