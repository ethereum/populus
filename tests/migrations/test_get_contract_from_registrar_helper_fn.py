import pytest

from populus import Project

from populus.utils.transactions import (
    wait_for_transaction_receipt,
    get_contract_address_from_txn,
)

from populus.migrations.registrar import get_contract_from_registrar


@pytest.fixture()
def prepared_project(project_dir, write_project_file, LIBRARY_13, MATH):
    write_project_file('contracts/Multiply13.sol', '\n'.join((
        LIBRARY_13['source'],
        MATH['source'],
    )))

    project = Project()

    assert 'Library13' in project.compiled_contracts
    assert 'Math' in project.compiled_contracts

    return project


@pytest.yield_fixture()
def deploy_chain(prepared_project):
    with prepared_project.get_chain('testrpc') as chain:
        yield chain


@pytest.fixture()
def math(deploy_chain):
    web3 = deploy_chain.web3

    Math = deploy_chain.contract_factories.Math
    MATH = deploy_chain.project.compiled_contracts['Math']

    math_deploy_txn_hash = Math.deploy()
    math_deploy_txn = web3.eth.getTransaction(math_deploy_txn_hash)
    math_13_address = get_contract_address_from_txn(web3, math_deploy_txn_hash, 30)

    assert math_deploy_txn['input'] == MATH['code']
    assert web3.eth.getCode(math_13_address) == MATH['code_runtime']

    return Math(address=math_13_address)


@pytest.fixture()
def library_13(deploy_chain):
    web3 = deploy_chain.web3

    Library13 = deploy_chain.contract_factories.Library13
    LIBRARY_13 = deploy_chain.project.compiled_contracts['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = get_contract_address_from_txn(web3, library_deploy_txn_hash, 30)

    assert library_deploy_txn['input'] == LIBRARY_13['code']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['code_runtime']

    return Library13(address=library_13_address)


def test_getting_contract_that_does_not_exist_in_registrar(deploy_chain):
    project = deploy_chain.project
    chain = deploy_chain

    actual = get_contract_from_registrar(
        chain=chain,
        contract_name='Library13',
        contract_factory=chain.contract_factories.Library13,
    )
    assert actual is None


def test_getting_contract_that_is_in_registrar(deploy_chain, library_13):
    project = deploy_chain.project
    chain = deploy_chain
    web3 = chain.web3
    registrar = chain.registrar

    register_txn = registrar.transact().setAddress('contract/Library13', library_13.address)
    wait_for_transaction_receipt(web3, register_txn, 30)

    actual = get_contract_from_registrar(
        chain=chain,
        contract_name='Library13',
        contract_factory=chain.contract_factories.Library13,
    )
    assert actual is not None
    assert actual.address == library_13.address


def test_getting_contract_that_is_in_registrar_with_bytecode_mismatch(deploy_chain, math):
    project = deploy_chain.project
    chain = deploy_chain
    web3 = chain.web3
    registrar = chain.registrar

    # register the wrong address.
    register_txn = registrar.transact().setAddress('contract/Library13', math.address)
    wait_for_transaction_receipt(web3, register_txn, 30)

    actual = get_contract_from_registrar(
        chain=chain,
        contract_name='Library13',
        contract_factory=chain.contract_factories.Library13,
    )
    assert actual is None


def test_getting_contract_that_is_in_registrar_with_empty_bytecode(deploy_chain):
    project = deploy_chain.project
    chain = deploy_chain
    web3 = chain.web3
    registrar = chain.registrar

    # register the wrong address.
    register_txn = registrar.transact().setAddress(
        'contract/Library13',
        '0xd3cda913deb6f67967b99d67acdfa1712c293601',
    )
    wait_for_transaction_receipt(web3, register_txn, 30)

    actual = get_contract_from_registrar(
        chain=chain,
        contract_name='Library13',
        contract_factory=chain.contract_factories.Library13,
    )
    assert actual is None
