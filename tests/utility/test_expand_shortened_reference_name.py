import pytest

from populus.utils.contracts import (
    expand_shortened_reference_name,
)

ALL_FULL_NAMES = (
    'ShortName',
    '__ShortName',
    'ShortName__',
    '__ShortName__',
    '_LongNameStartsWithUnderscore1234567890123456789012345678901234567890',
    'LongName1234567890123456789012345678901234567890123456789012345678901',
    'EndsWithUnderscores__________________________________________________',
    '____StartsAndEndsWithUnderscores_____________________________________',
)

@pytest.mark.parametrize(
    'name',
    ALL_FULL_NAMES,
)
def test_expand_shortened_reference_names(name):
    short_name = name[:36]
    actual = expand_shortened_reference_name(short_name, ALL_FULL_NAMES)
    assert actual == name
