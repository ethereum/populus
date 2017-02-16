import pytest

from populus.contracts.exceptions import (
    UnknownContract,
)


@pytest.yield_fixture()
def tester_chain(project):
    assert 'Math' in project.compiled_contracts
    assert 'Library13' in project.compiled_contracts
    assert 'Multiply13' in project.compiled_contracts

    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def math(tester_chain):
    chain = tester_chain
    web3 = chain.web3

    Math = chain.base_contract_factories.Math
    MATH = chain.project.compiled_contract_data['Math']

    math_deploy_txn_hash = Math.deploy()
    math_deploy_txn = web3.eth.getTransaction(math_deploy_txn_hash)
    math_address = chain.wait.for_contract_address(math_deploy_txn_hash, timeout=30)

    assert math_deploy_txn['input'] == MATH['bytecode']
    assert web3.eth.getCode(math_address) == MATH['bytecode_runtime']

    return Math(address=math_address)


@pytest.fixture()
def math(tester_chain):
    chain = tester_chain
    web3 = chain.web3

    Library13 = chain.base_contract_factories.Library13
    LIBRARY_13 = chain.project.compiled_contract_data['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash, timeout=30)

    assert library_deploy_txn['input'] == LIBRARY_13['code']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['code_runtime']

    return Library13(address=library_13_address)


def test_unknown_contract(tester_chain):
    chain = tester_chain
    provider = chain.store.provider

    with pytest.raises(UnknownContract):
        provider.get_or_deploy_contract('NotAKnownContract')


def test_it_uses_existing_address(tester_chain, math):
    chain = tester_chain
    provider = chain.store.provider
    registrar = chain.store.registrar

    registrar.set_contract_address('Math', math.address)

    actual_math, created = provider.get_or_deploy_contract('Math')
    assert actual_math.address == math.address
    assert created is None


def test_it_lazily_deploys_contract(tester_chain):
    chain = tester_chain
    provider = chain.store.provider

    math, created = provider.get_or_deploy_contract('Math')
    assert math.address

    assert 'Math' in provider.deployed_contracts
    assert created is not None


def test_it_handles_library_dependencies(tester_chain):
    chain = tester_chain
    provider = chain.store.provider

    multiply_13, created = provider.get_or_deploy_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39
    assert created is not None


def test_it_uses_existing_library_dependencies(tester_chain, library_13):
    chain = tester_chain
    provider = chain.store.provider
    registrar = chain.store.registrar

    registrar.set_contract_address('Library13', library_13.address)

    multiply_13, created = provider.get_or_deploy_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39
    assert created is not None

    chain_bytecode = chain.web3.eth.getCode(multiply_13.address)
    assert library_13.address[2:] in chain_bytecode
