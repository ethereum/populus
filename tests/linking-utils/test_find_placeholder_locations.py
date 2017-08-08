import pytest

from populus.utils.linking import (
    find_placeholder_locations,
)


CODE = "0x60606040526101af806100126000396000f3606060405260e060020a600035046330fd609b81146100475780637a8ebf591461008f578063a95f5076146100d7578063db81daaa1461011f578063e7f09e0514610167575b005b61004560e260020a6303155a6702606090815273__Has_Underscores_In_The_Name___________90630c55699c906064906000906004818660325a03f41561000257505050565b61004560e260020a6303155a6702606090815273___StartsWithUnderscore_________________90630c55699c906064906000906004818660325a03f41561000257505050565b61004560e260020a6303155a6702606090815273__LongerThan40Characters12345678901234__90630c55699c906064906000906004818660325a03f41561000257505050565b61004560e260020a6303155a6702606090815273__B1____________________________________90630c55699c906064906000906004818660325a03f41561000257505050565b61004560e260020a6303155a6702606090815273__A_____________________________________90630c55699c906064906000906004818660325a03f4156100025750505056"  # noqa: E501


@pytest.mark.parametrize(
    'bytecode,expected',
    (
        ('0x', tuple()),
        ('', tuple()),
        (
            '0x__NothingButLink________________________',
            (
                ('NothingButLink', 0, 40),
            ),
        ),
        (
            '0xabcdef__MathLib_______________________________12345',
            (
                ('MathLib', 6, 40),
            ),
        ),
        (
            '0xabcdef__Some32ByteValue_______________________12345',
            (
                ('Some32ByteValue', 6, 40),
            )
        ),
        (
            '0xabcdef__Close___________________________________Together______________________________abcdef',  # noqa: E501
            (
                ('Close', 6, 40),
                ('Together', 46, 40),
            )
        ),
        (
            CODE,
            (
                ('Has_Underscores_In_The_Name', 220, 40),
                ('_StartsWithUnderscore', 364, 40),
                ('LongerThan40Characters12345678901234', 508, 40),
                ('B1', 652, 40),
                ('A', 796, 40),
            )
        ),
    ),
)
def test_find_placeholder_locations(bytecode, expected):
    actual = find_placeholder_locations(bytecode)

    assert len(actual) == len(expected)

    for left, right in zip(actual, expected):
        assert left == right
