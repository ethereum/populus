import pytest

from populus.contracts.exceptions import (
    UnknownContract,
)


def test_unknown_contract(chain):
    provider = chain.store.provider

    with pytest.raises(UnknownContract):
        provider.get_or_deploy_contract('NotAKnownContract')


def test_it_uses_existing_address(chain, math):
    provider = chain.store.provider
    registrar = chain.store.registrar

    registrar.set_contract_address('Math', math.address)

    actual_math, created = provider.get_or_deploy_contract('Math')
    assert actual_math.address == math.address
    assert created is None


def test_it_lazily_deploys_contract(chain):
    provider = chain.store.provider

    math, created = provider.get_or_deploy_contract('Math')
    assert math.address

    assert 'Math' in provider.deployed_contracts
    assert created is not None


def test_it_handles_library_dependencies(chain):
    provider = chain.store.provider

    multiply_13, created = provider.get_or_deploy_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39
    assert created is not None


def test_it_uses_existing_library_dependencies(chain, library_13):
    provider = chain.store.provider
    registrar = chain.store.registrar

    registrar.set_contract_address('Library13', library_13.address)

    multiply_13, created = provider.get_or_deploy_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39
    assert created is not None

    chain_bytecode = chain.web3.eth.getCode(multiply_13.address)
    assert library_13.address[2:] in chain_bytecode
