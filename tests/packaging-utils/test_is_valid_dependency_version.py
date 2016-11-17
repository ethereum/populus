import pytest

from populus.utils.packaging import (
    is_valid_dependency_version,
)


@pytest.mark.parametrize(
    "value,expected",
    (
        # Good
        ('1.0.0', True),
        ('1.0.0-beta1', True),
        ('1.0.0-beta1+d3af3487', True),
        ('>1.0.0', True),
        ('>=1.0.0', True),
        ('<1.0.0', True),
        ('<=1.0.0', True),
        # Bad
        ('==1.0.0', False),
    )
)
def test_is_valid_dependency_version(value, expected):
    actual = is_valid_dependency_version(value)
    assert actual is expected
