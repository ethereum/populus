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
def register_address(tester_chain):
    chain = tester_chain
    def _register_address(name, value):
        if name.startswith('contract/'):
            contract_key = name
        else:
            contract_key = 'contract/{name}'.format(name=name)
        register_txn_hash = tester_chain.registrar.transact().setAddress(
            contract_key, value,
        )
        chain.wait.for_receipt(register_txn_hash, timeout=120)
    return _register_address


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


@pytest.fixture()
def library_13(tester_chain):
    chain = tester_chain
    web3 = chain.web3

    Library13 = chain.contract_factories.Library13
    LIBRARY_13 = chain.project.compiled_contracts['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash, timeout=30)

    assert library_deploy_txn['input'] == LIBRARY_13['code']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['code_runtime']

    return Library13(address=library_13_address)


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
