import pytest


def test_getting_contract_data(chain, math):
    provider = chain.provider

    contract_data = provider.get_contract_data('Math')
    assert math.bytecode == contract_data['bytecode']
