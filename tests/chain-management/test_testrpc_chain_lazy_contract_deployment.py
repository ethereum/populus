import pytest

from populus import Project
from populus.chain import UnknownContract
from populus.utils.transactions import (
    wait_for_transaction_receipt,
    get_contract_address_from_txn,
)


@pytest.yield_fixture()
def testrpc_chain(project_dir, write_project_file, MATH, LIBRARY_13, MULTIPLY_13):
    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file(
        'contracts/Multiply13.sol',
        '\n'.join((LIBRARY_13['source'], MULTIPLY_13['source'])),
    )

    project = Project()

    assert 'Math' in project.compiled_contracts
    assert 'Library13' in project.compiled_contracts
    assert 'Multiply13' in project.compiled_contracts

    with project.get_chain('testrpc') as chain:
        yield chain


@pytest.fixture()
def register_address(testrpc_chain):
    def _register_address(name, value):
        if name.startswith('contract/'):
            contract_key = name
        else:
            contract_key = 'contract/{name}'.format(name=name)
        register_txn_hash = testrpc_chain.registrar.transact().setAddress(
            contract_key, value,
        )
        wait_for_transaction_receipt(testrpc_chain.web3, register_txn_hash, 120)
    return _register_address


@pytest.fixture()
def math(testrpc_chain):
    web3 = testrpc_chain.web3

    Math = testrpc_chain.contract_factories.Math
    MATH = testrpc_chain.project.compiled_contracts['Math']

    math_deploy_txn_hash = Math.deploy()
    math_deploy_txn = web3.eth.getTransaction(math_deploy_txn_hash)
    math_address = get_contract_address_from_txn(web3, math_deploy_txn_hash, 30)

    assert math_deploy_txn['input'] == MATH['code']
    assert web3.eth.getCode(math_address) == MATH['code_runtime']

    return Math(address=math_address)


@pytest.fixture()
def library_13(testrpc_chain):
    web3 = testrpc_chain.web3

    Library13 = testrpc_chain.contract_factories.Library13
    LIBRARY_13 = testrpc_chain.project.compiled_contracts['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = get_contract_address_from_txn(web3, library_deploy_txn_hash, 30)

    assert library_deploy_txn['input'] == LIBRARY_13['code']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['code_runtime']

    return Library13(address=library_13_address)


def test_unknown_contract(testrpc_chain):
    chain = testrpc_chain

    with pytest.raises(UnknownContract):
        chain.get_contract('NotAKnownContract')


def test_it_uses_existing_address(testrpc_chain, math, register_address):
    chain = testrpc_chain

    register_address('contract/Math', math.address)
    # sanity check
    assert chain.registrar.call().exists('contract/Math')

    actual_math = chain.get_contract('Math')
    assert actual_math.address == math.address


def test_it_lazily_deploys_contract(testrpc_chain):
    chain = testrpc_chain

    math = chain.get_contract('Math')
    assert math.address

    assert 'Math' in chain.deployed_contracts


def test_it_handles_library_dependencies(testrpc_chain):
    chain = testrpc_chain

    multiply_13 = chain.get_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39


def test_it_uses_existing_library_dependencies(testrpc_chain, library_13,
                                               register_address):
    chain = testrpc_chain

    register_address('contract/Library13', library_13.address)
    # sanity check
    assert chain.registrar.call().exists('contract/Library13')

    multiply_13 = chain.get_contract('Multiply13')
    assert multiply_13.call().multiply13(3) == 39

    chain_bytecode = chain.web3.eth.getCode(multiply_13.address)
    assert library_13.address[2:] in chain_bytecode
