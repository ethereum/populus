import string

from hypothesis import (
    given,
    strategies as st,
)
import pytest

from populus.utils.linking import (
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


@given(
    full_names=st.lists(
        st.text(
            alphabet=string.digits + string.ascii_letters + '_',
            min_size=1,
            max_size=100,
        ).filter(lambda s: not s[0].isdigit()),
        min_size=1,
        max_size=10,
        unique=True,
    )
)
def test_round_trip_always_possible(full_names):
    expected = set(full_names)
    actual = {
        expand_shortened_reference_name(name[:36], full_names)
        for name in full_names
    }
    assert actual == expected
