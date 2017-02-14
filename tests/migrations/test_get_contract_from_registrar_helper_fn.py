import pytest

from populus import Project

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
    chain = deploy_chain
    web3 = chain.web3

    Math = chain.contract_factories.Math
    MATH = chain.project.compiled_contracts['Math']

    math_deploy_txn_hash = Math.deploy()
    math_deploy_txn = web3.eth.getTransaction(math_deploy_txn_hash)
    math_13_address = chain.wait.for_contract_address(math_deploy_txn_hash, timeout=30)

    assert math_deploy_txn['input'] == MATH['bytecode']
    assert web3.eth.getCode(math_13_address) == MATH['bytecode_runtime']

    return Math(address=math_13_address)


@pytest.fixture()
def library_13(deploy_chain):
    chain = deploy_chain
    web3 = chain.web3

    Library13 = chain.contract_factories.Library13
    LIBRARY_13 = chain.project.compiled_contracts['Library13']

    library_deploy_txn_hash = Library13.deploy()
    library_deploy_txn = web3.eth.getTransaction(library_deploy_txn_hash)
    library_13_address = chain.wait.for_contract_address(library_deploy_txn_hash, timeout=30)

    assert library_deploy_txn['input'] == LIBRARY_13['bytecode']
    assert web3.eth.getCode(library_13_address) == LIBRARY_13['bytecode_runtime']

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
    chain = deploy_chain
    project = chain.project
    web3 = chain.web3
    registrar = chain.registrar

    register_txn = registrar.transact().setAddress('contract/Library13', library_13.address)
    chain.wait.for_receipt(register_txn, timeout=30)

    actual = get_contract_from_registrar(
        chain=chain,
        contract_name='Library13',
        contract_factory=chain.contract_factories.Library13,
    )
    assert actual is not None
    assert actual.address == library_13.address


def test_getting_contract_that_is_in_registrar_with_bytecode_mismatch(deploy_chain, math):
    chain = deploy_chain
    project = chain.project
    web3 = chain.web3
    registrar = chain.registrar

    # register the wrong address.
    register_txn = registrar.transact().setAddress('contract/Library13', math.address)
    chain.wait.for_receipt(register_txn, timeout=30)

    actual = get_contract_from_registrar(
        chain=chain,
        contract_name='Library13',
        contract_factory=chain.contract_factories.Library13,
    )
    assert actual is None


def test_getting_contract_that_is_in_registrar_with_empty_bytecode(deploy_chain):
    chain = deploy_chain
    project = chain.project
    web3 = chain.web3
    registrar = chain.registrar

    # register the wrong address.
    register_txn = registrar.transact().setAddress(
        'contract/Library13',
        '0xd3cda913deb6f67967b99d67acdfa1712c293601',
    )
    chain.wait.for_receipt(register_txn, timeout=30)

    actual = get_contract_from_registrar(
        chain=chain,
        contract_name='Library13',
        contract_factory=chain.contract_factories.Library13,
    )
    assert actual is None
