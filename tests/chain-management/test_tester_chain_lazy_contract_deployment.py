import pytest

from populus import Project
from populus.chain import UnknownContract


@pytest.yield_fixture()
def tester_chain(project_dir, write_project_file, MATH, LIBRARY_13, MULTIPLY_13):
    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file(
        'contracts/Multiply13.sol',
        '\n'.join((LIBRARY_13['source'], MULTIPLY_13['source'])),
    )

    project = Project()

    assert 'Math' in project.compiled_contracts
    assert 'Library13' in project.compiled_contracts
    assert 'Multiply13' in project.compiled_contracts

    with project.get_chain('tester') as chain:
        yield chain


@pytest.fixture()
def math(tester_chain):
    chain = tester_chain
    web3 = chain.web3

    Math = chain.contract_factories.Math
    MATH = chain.project.compiled_contracts['Math']

    math_deploy_txn_hash = Math.deploy()
    math_deploy_txn = web3.eth.getTransaction(math_deploy_txn_hash)
    math_address = chain.wait.for_contract_address(math_deploy_txn_hash, timeout=30)

    assert math_deploy_txn['input'] == MATH['code']
    assert web3.eth.getCode(math_address) == MATH['code_runtime']

    return Math(address=math_address)


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
