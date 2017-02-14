import pytest

from populus import Project
from populus.chain import UnknownContract


def test_unknown_contract(tester_chain):
    chain = tester_chain

    with pytest.raises(UnknownContract):
        chain.get_contract('NotAKnownContract')


def test_it_uses_existing_address(tester_chain, math, register_address):
    chain = tester_chain

    register_address('contract/Math', math.address)
    # sanity check
    assert chain.registrar.call().exists('contract/Math')

    actual_math = chain.get_contract('Math')
    assert actual_math.address == math.address


def test_it_lazily_deploys_contract(tester_chain):
    chain = tester_chain

    math = chain.get_contract('Math')
    assert math.address

    assert 'Math' in chain.deployed_contracts


def test_it_handles_library_dependencies(tester_chain):
    chain = tester_chain

    multiply_13 = chain.get_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39


def test_it_uses_existing_library_dependencies(tester_chain, library_13,
                                               register_address):
    chain = tester_chain

    register_address('contract/Library13', library_13.address)
    # sanity check
    assert chain.registrar.call().exists('contract/Library13')

    multiply_13 = chain.get_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39

    chain_bytecode = chain.web3.eth.getCode(multiply_13.address)
    assert library_13.address[2:] in chain_bytecode
