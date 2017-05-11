import pytest

import json

from populus.utils.linking import (
    link_bytecode_by_name,
)
from populus import Project


@pytest.fixture(autouse=True)
def inject_contracts(request):
    test_fn = request.function
    if not hasattr(test_fn, '_populus_contract_fixtures'):
        test_fn._populus_contract_fixtures = []
    for fixture_path in ('Math.sol', 'Library13.sol', 'Multiply13.sol'):
        if fixture_path not in test_fn._populus_contract_fixtures:
            test_fn._populus_contract_fixtures.append(fixture_path)


@pytest.yield_fixture()
def temp_chain(project, wait_for_unlock):
    assert 'Math' in project.compiled_contract_data
    assert 'Library13' in project.compiled_contract_data
    assert 'Multiply13' in project.compiled_contract_data

    with project.get_chain('temp') as chain:
        wait_for_unlock(chain.web3)
        yield chain


@pytest.fixture()
def math(temp_chain):
    chain = temp_chain
    web3 = chain.web3

    Math = chain.contract_factories.Math
    MATH = chain.project.compiled_contract_data['Math']

    math_deploy_txn_hash = Math.deploy()
    math_deploy_txn = web3.eth.getTransaction(math_deploy_txn_hash)
    math_address = chain.wait.for_contract_address(math_deploy_txn_hash)

    assert math_deploy_txn['input'] == MATH['bytecode']
    assert web3.eth.getCode(math_address) == MATH['bytecode_runtime']

    return Math(address=math_address)


@pytest.fixture()
def library_13(temp_chain):
    chain = temp_chain
    web3 = chain.web3

    Library13 = chain.contract_factories.Library13
    LIBRARY_13 = chain.project.compiled_contract_data['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash)

    assert library_deploy_txn['input'] == LIBRARY_13['bytecode']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['bytecode_runtime']

    return Library13(address=library_13_address)


@pytest.fixture()
def multiply_13(temp_chain, library_13):
    chain = temp_chain
    web3 = chain.web3

    Multiply13 = chain.contract_factories['Multiply13']

    bytecode = link_bytecode_by_name(Multiply13.bytecode, Library13=library_13.address)
    bytecode_runtime = link_bytecode_by_name(Multiply13.bytecode_runtime, Library13=library_13.address)

    LinkedMultiply13 = chain.web3.eth.contract(
        abi=Multiply13.abi,
        bytecode=bytecode,
        bytecode_runtime=bytecode_runtime,
        source=Multiply13.source,
    )

    multiply_13_deploy_txn_hash = LinkedMultiply13.deploy()
    multiply_13_deploy_txn = web3.eth.getTransaction(multiply_13_deploy_txn_hash)
    multiply_13_address = chain.wait.for_contract_address(multiply_13_deploy_txn_hash)

    assert multiply_13_deploy_txn['input'] == LinkedMultiply13.bytecode
    assert web3.eth.getCode(multiply_13_address) == LinkedMultiply13.bytecode_runtime

    return LinkedMultiply13(address=multiply_13_address)


@pytest.fixture()
def register_address(temp_chain):
    chain = temp_chain

    def _register_address(name, value):
        register_txn_hash = temp_chain.registrar.transact().setAddress(
            'contract/{name}'.format(name=name), value,
        )
        chain.wait.for_receipt(register_txn_hash)
    return _register_address
