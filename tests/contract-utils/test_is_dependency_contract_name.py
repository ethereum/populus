import pytest

from populus.utils.contracts import (
    is_dependency_contract_name,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        ('owned', False),
        ('owned:owned', True),
        ('Owned:owned', False),
        ('owned:owned-with-hyphen', False),
    )
)
def testis_dependency_contract_name(value, expected):
    actual = is_dependency_contract_name(value)
    assert actual is expected
