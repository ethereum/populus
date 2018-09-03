import pytest

from populus.contracts.exceptions import (
    UnknownContract,
)
from populus.utils.hexadecimal import hexbytes_to_hexstr


def test_unknown_contract(chain):
    provider = chain.provider

    with pytest.raises(UnknownContract):
        provider.get_or_deploy_contract('NotAKnownContract')


def test_it_uses_existing_address(chain, math):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Math', math.address)

    actual_math, deploy_txn = provider.get_or_deploy_contract('Math')
    assert actual_math.address == math.address
    assert deploy_txn is None


def test_it_lazily_deploys_contract(chain):
    provider = chain.provider

    assert provider.is_contract_available('Math') is False
    math, created = provider.get_or_deploy_contract('Math')

    assert math.address
    assert provider.is_contract_available('Math') is True
    assert created is not None


def test_it_handles_library_dependencies(chain):
    provider = chain.provider

    multiply_13, deploy_txn = provider.get_or_deploy_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39
    assert deploy_txn is not None


def test_it_uses_existing_library_dependencies(chain, library_13):
    provider = chain.provider
    registrar = chain.registrar

    registrar.set_contract_address('Library13', library_13.address)

    multiply_13, deploy_txn = provider.get_or_deploy_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39
    assert deploy_txn is not None

    chain_bytecode = chain.web3.eth.getCode(multiply_13.address)
    assert library_13.address[2:].lower() in hexbytes_to_hexstr(chain_bytecode)
