import pytest

from populus.project import Project


def test_project_contract_factories_property(project_dir, write_project_file,
                                             MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    project = Project()
    with project.get_chain('testrpc') as chain:
        assert chain.contract_factories.Math.abi == MATH['abi']
        assert chain.contract_factories.Math.code == MATH['code']
        assert chain.contract_factories.Math.code_runtime == MATH['code_runtime']
