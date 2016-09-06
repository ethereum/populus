import pytest

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
def library_13(testrpc_chain):
    chain= testrpc_chain
    web3 = chain.web3

    Library13 = chain.contract_factories.Library13

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash, timeout=30)

    assert library_deploy_txn['input'] == Library13.code
    assert web3.eth.getCode(library_13_address) == Library13.code_runtime

    return Library13(address=library_13_address)


def test_get_contract_factory_with_no_dependencies(testrpc_chain):
    chain = testrpc_chain

    MATH = chain.project.compiled_contracts['Math']
    Math = chain.get_contract_factory('Math')

    assert Math.code == MATH['code']
    assert Math.code_runtime == MATH['code_runtime']


def test_get_contract_factory_with_missing_dependency(testrpc_chain):
    chain = testrpc_chain

    with pytest.raises(NoKnownAddress):
        Multiply13 = chain.get_contract_factory('Multiply13')



def test_get_contract_factory_with_declared_dependency(testrpc_chain):
    chain = testrpc_chain

    MULTIPLY_13 = chain.project.compiled_contracts['Multiply13']
    Multiply13 = chain.get_contract_factory(
        'Multiply13',
        link_dependencies={
            'Library13': '0xd3cda913deb6f67967b99d67acdfa1712c293601',
        },
    )

    expected_code = link_bytecode(MULTIPLY_13['code'], Library13='0xd3cda913deb6f67967b99d67acdfa1712c293601')
    expected_runtime = link_bytecode(MULTIPLY_13['code_runtime'], Library13='0xd3cda913deb6f67967b99d67acdfa1712c293601')

    assert Multiply13.code == expected_code
    assert Multiply13.code_runtime == expected_runtime


def test_get_contract_factory_with_registrar_dependency(testrpc_chain,
                                                        library_13):
    chain = testrpc_chain
    registrar = chain.registrar

    register_txn_hash = registrar.transact().setAddress(
        'contract/Library13', library_13.address,
    )

    chain.wait.for_receipt(register_txn_hash)

    MULTIPLY_13 = chain.project.compiled_contracts['Multiply13']
    Multiply13 = chain.get_contract_factory('Multiply13')

    expected_code = link_bytecode(MULTIPLY_13['code'], Library13=library_13.address)
    expected_runtime = link_bytecode(MULTIPLY_13['code_runtime'], Library13=library_13.address)

    assert Multiply13.code == expected_code
    assert Multiply13.code_runtime == expected_runtime


def test_with_bytecode_mismatch_in_registrar_dependency(testrpc_chain,
                                                        library_13):
    chain = testrpc_chain
    registrar = chain.registrar

    # this will not match the expected underlying bytecode for the Library13
    # contract so it will cause a failure.
    register_txn_hash = registrar.transact().setAddress(
        'contract/Library13', '0xd3cda913deb6f67967b99d67acdfa1712c293601'
    )

    chain.wait.for_receipt(register_txn_hash)

    with pytest.raises(BytecodeMismatchError):
        chain.get_contract_factory('Multiply13')
