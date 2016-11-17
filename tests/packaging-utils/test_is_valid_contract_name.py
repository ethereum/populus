import pytest

from populus.utils.packaging import is_valid_contract_name


@pytest.mark.parametrize(
    'value,expected',
    (
        ('MyContract', True),
        ('MyContract99', True),
        ('myContract', True),
        ('_myContract', True),
        ('My_Contract', True),
        ('__MyContract__', True),
        # bad
        ('0MyContract', False),
        ('-MyContract', False),
        ('My*Contract', False),
    )
)
def test_is_valid_contract_name(value, expected):
    actual = is_valid_contract_name(value)
    assert actual is expected

