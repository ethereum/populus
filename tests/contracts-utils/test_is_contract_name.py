import pytest

from populus.utils.contracts import (
    is_contract_name,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        ('A', True),
        ('a', True),
        ('_', True),
        ('somecontract', True),
        ('SomeContract', True),
        ('someContract', True),
        ('some_contract', True),
        ('Some_Contract', True),
        ('Some_Contract__', True),
        ('SomeContract99', True),
        ('_LeadingUnderscore', True),
        ('9', False),
        ('With-Dash', False)
    )
)
def test_is_contract_name(value, expected):
    actual = is_contract_name(value)
    assert actual is expected
