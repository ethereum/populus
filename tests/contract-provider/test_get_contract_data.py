import pytest


def test_getting_contract_data(chain, provider, math):

    contract_data = provider.get_contract_data('Math')
    assert math.bytecode == contract_data['bytecode']
