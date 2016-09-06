import pytest

from populus.utils.contracts import (
    link_bytecode,
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
    chain = testrpc_chain
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
def library_13(testrpc_chain):
    chain = testrpc_chain
    web3 = chain.web3

    Library13 = chain.contract_factories.Library13
    LIBRARY_13 = chain.project.compiled_contracts['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash, timeout=30)

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
    multiply_13_address = chain.wait.for_contract_address(multiply_13_deploy_txn_hash, timeout=30)

    assert multiply_13_deploy_txn['input'] == LinkedMultiply13.code
    assert web3.eth.getCode(multiply_13_address) == LinkedMultiply13.code_runtime

    return LinkedMultiply13(address=multiply_13_address)


@pytest.fixture()
def register_address(testrpc_chain):
    chain = testrpc_chain

    def _register_address(name, value):
        register_txn_hash = testrpc_chain.registrar.transact().setAddress(
            'contract/{name}'.format(name=name), value,
        )
        chain.wait.for_receipt(register_txn_hash, timeout=120)
    return _register_address


def test_contract_availability_with_no_dependencies(testrpc_chain, math, register_address):
    chain = testrpc_chain

    register_address('Math', math.address)

    is_available = chain.is_contract_available('Math')
    assert is_available is True


def test_contract_availability_when_not_registered(testrpc_chain):
    chain = testrpc_chain

    is_available = chain.is_contract_available('Math')
    assert is_available is False


def test_contract_availability_with_missing_dependency(testrpc_chain,
                                                       multiply_13,
                                                       register_address):
    chain = testrpc_chain

    register_address('Multiply13', multiply_13.address)

    is_available = chain.is_contract_available('Multiply13')
    assert is_available is False


def test_contract_availability_with_bytecode_mismatch(testrpc_chain,
                                                      library_13,
                                                      math,
                                                      register_address):
    chain = testrpc_chain

    register_address('Math', library_13.address)

    is_available = chain.is_contract_available('Math')
    assert is_available is False


def test_contract_availability_skipping_bytecode_validation(testrpc_chain,
                                                            library_13,
                                                            math,
                                                            register_address):
    chain = testrpc_chain

    register_address('Math', library_13.address)

    is_available = chain.is_contract_available('Math', validate_bytecode=False)
    assert is_available is True


def test_contract_availability_with_bytecode_mismatch_on_dependency(testrpc_chain,
                                                                    multiply_13,
                                                                    math,
                                                                    register_address):
    chain = testrpc_chain

    register_address('Multiply13', multiply_13.address)
    register_address('Library13', math.address)

    is_available = chain.is_contract_available('Multiply13')
    assert is_available is False


def test_contract_availability_with_dependency(testrpc_chain,
                                               multiply_13,
                                               library_13,
                                               register_address):
    chain = testrpc_chain

    register_address('Multiply13', multiply_13.address)
    register_address('Library13', library_13.address)

    is_available = chain.is_contract_available('Multiply13')
    assert is_available is True


def test_contract_availability_with_declared_dependency(testrpc_chain,
                                                        multiply_13,
                                                        library_13,
                                                        register_address):
    chain = testrpc_chain

    register_address('Multiply13', multiply_13.address)

    is_available = chain.is_contract_available(
        'Multiply13',
        link_dependencies={'Library13': library_13.address},
    )
    assert is_available is True
