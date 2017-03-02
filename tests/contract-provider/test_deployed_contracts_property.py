import pytest

from populus.contracts.exceptions import (
    NoKnownAddress,
)


def test_with_no_deployed_contracts(chain, math):
    provider = chain.provider

    assert len(provider.deployed_contracts) == 0


def test_with_single_deployed_contract(chain, math):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Math', math.address)

    assert len(provider.deployed_contracts) == 1
    assert 'Math' in provider.deployed_contracts
    assert provider.deployed_contracts.Math.call().multiply7(3) == 21


def test_with_multiple_deployed_contracts(chain,
                                          math,
                                          library_13,
                                          multiply_13):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Math', math.address)
    registrar.set_contract_address('Library13', library_13.address)
    registrar.set_contract_address('Multiply13', multiply_13.address)

    assert len(provider.deployed_contracts) == 3

    assert 'Math' in provider.deployed_contracts
    assert provider.deployed_contracts.Math.call().multiply7(3) == 21

    assert 'Library13' in provider.deployed_contracts
    assert provider.deployed_contracts.Library13.call().multiply13(3) == 39

    assert 'Multiply13' in provider.deployed_contracts
    assert provider.deployed_contracts.Multiply13.call().multiply13(3) == 39


def test_contracts_with_missing_dependencies_ignored(chain,
                                                     math,
                                                     library_13,
                                                     multiply_13):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Math', math.address)
    registrar.set_contract_address('Multiply13', multiply_13.address)

    assert len(provider.deployed_contracts) == 1

    assert 'Math' in provider.deployed_contracts
    assert provider.deployed_contracts.Math.call().multiply7(3) == 21

    assert 'Library13' not in provider.deployed_contracts
    assert 'Multiply13' not in provider.deployed_contracts
