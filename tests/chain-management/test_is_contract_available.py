import pytest

from populus import Project


@pytest.yield_fixture()
def testrpc_chain(project_dir, write_project_file, MATH, LIBRARY_13):
    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file('contracts/Library13.sol', LIBRARY_13['source'])

    project = Project()

    assert 'Math' in project.compiled_contracts
    assert 'Library13' in project.compiled_contracts

    with project.get_chain('testrpc') as chain:
        yield chain


def test_testrpc_chain_has_registrar(project_dir, testrpc_chain):
    project = Project()
    chain = testrpc_chain

    assert chain.is_contract_available('Math') is False
