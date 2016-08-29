import pytest

from populus.utils.transactions import (
    wait_for_transaction_receipt,
    get_contract_address_from_txn,
)
from populus.utils.contracts import (
    link_bytecode,
)
from populus.chain import (
    NoKnownAddress,
    BytecodeMismatchError,
)
from populus import Project


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


@pytest.fixture()
def multiply_13(testrpc_chain, library_13):
    chain = testrpc_chain
    web3 = chain.web3

    Multiply13 = chain.contract_factories['Multiply13']

    code = link_bytecode(Multiply13.code, Library13=library_13.address)
    code_runtime = link_bytecode(Multiply13.code_runtime, Library13=library_13.address)

    LinkedMultiply13 = chain.web3.eth.contract(
        abi=Multiply13.abi,
        code=code,
        code_runtime=code_runtime,
        source=Multiply13.source,
    )

    multiply_13_deploy_txn_hash = LinkedMultiply13.deploy()
    multiply_13_deploy_txn = web3.eth.getTransaction(multiply_13_deploy_txn_hash)
    multiply_13_address = get_contract_address_from_txn(web3, multiply_13_deploy_txn_hash, 30)

    assert multiply_13_deploy_txn['input'] == LinkedMultiply13.code
    assert web3.eth.getCode(multiply_13_address) == LinkedMultiply13.code_runtime

    return LinkedMultiply13(address=multiply_13_address)


@pytest.fixture()
def register_address(testrpc_chain):
    def _register_address(name, value):
        register_txn_hash = testrpc_chain.registrar.transact().setAddress(
            'contract/{name}'.format(name=name), value,
        )
        wait_for_transaction_receipt(testrpc_chain.web3, register_txn_hash, 120)
    return _register_address


def test_with_no_deployed_contracts(testrpc_chain, math, register_address):
    chain = testrpc_chain

    assert len(chain.deployed_contracts) == 0


def test_with_single_deployed_contract(testrpc_chain, math, register_address):
    chain = testrpc_chain

    register_address('Math', math.address)

    assert len(chain.deployed_contracts) == 1
    assert 'Math' in chain.deployed_contracts
    assert chain.deployed_contracts.Math.call().multiply7(3) == 21


def test_with_multiple_deployed_contracts(testrpc_chain,
                                          math,
                                          library_13,
                                          multiply_13,
                                          register_address):
    chain = testrpc_chain

    register_address('Math', math.address)
    register_address('Library13', library_13.address)
    register_address('Multiply13', multiply_13.address)

    assert len(chain.deployed_contracts) == 3

    assert 'Math' in chain.deployed_contracts
    assert chain.deployed_contracts.Math.call().multiply7(3) == 21

    assert 'Library13' in chain.deployed_contracts
    assert chain.deployed_contracts.Library13.call().multiply13(3) == 39

    assert 'Multiply13' in chain.deployed_contracts
    assert chain.deployed_contracts.Multiply13.call().multiply13(3) == 39


def test_missing_dependencies_ignored(testrpc_chain,
                                      math,
                                      library_13,
                                      multiply_13,
                                      register_address):
    chain = testrpc_chain

    register_address('Math', math.address)
    register_address('Multiply13', multiply_13.address)

    assert len(chain.deployed_contracts) == 1

    assert 'Math' in chain.deployed_contracts
    assert chain.deployed_contracts.Math.call().multiply7(3) == 21

    assert 'Library13' not in chain.deployed_contracts
    assert 'Multiply13' not in chain.deployed_contracts
