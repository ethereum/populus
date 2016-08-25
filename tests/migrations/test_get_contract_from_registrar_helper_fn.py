import pytest

from populus import Project

from populus.migrations.registrar import get_contract_from_registrar


@pytest.fixture()
def prepared_project(project_dir, write_project_file, LIBRARY_13, MULTIPLY_13):
    write_project_file('contracts/Multiply13.sol', '\n'.join((
        LIBRARY_13['source'],
        MULTIPLY_13['source'],
    )))

    project = Project()

    assert 'Library13' in project.compiled_contracts
    assert 'Multiply13' in project.compiled_contracts

    return project


@pytest.yield_fixture()
def deploy_chain(prepared_project):
    with prepared_project.get_chain('testrpc') as chain:
        yield chain


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
    deploy_chain.web3

    actual = get_contract_from_registrar(
        chain=chain,
        contract_name='Library13',
        contract_factory=chain.contract_factories.Library13,
    )
    assert actual is None
