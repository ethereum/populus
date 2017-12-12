import pytest

from populus.utils.contracts import (
    is_contract_name,
)


@pytest.mark.parametrize(
    'value,expected',
    (
        pytest.param('A', True, id='cap-A'),
        pytest.param('a', True, id='lower-a'),
        ('_', True),
        pytest.param('somecontract', True, id='all-lower'),
        pytest.param('SomeContract', True, id='upper-word'),
        pytest.param('someContract', True, id='lower-first'),
        pytest.param('some_contract', True, id='underscore-word-sep-lower'),
        pytest.param('Some_Contract', True, id='underscore-word-sep-upper'),
        ('Some_Contract__', True),
        ('SomeContract99', True),
        ('_LeadingUnderscore', True),
        ('9', False),
        ('With-Dash', False)
    ),
)
def test_is_contract_name(value, expected):
    actual = is_contract_name(value)
    assert actual is expected
