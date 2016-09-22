import pytest

from populus.project import Project


def test_project_compiled_contracts_with_no_default_env(project_dir,
                                                        write_project_file,
                                                        MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    project = Project()

    assert 'Math' in project.compiled_contracts
    assert 'code' in project.compiled_contracts['Math']
    assert 'code_runtime' in project.compiled_contracts['Math']
    assert 'abi' in project.compiled_contracts['Math']

    compiled_contracts_object_id = id(project.compiled_contracts)

    assert id(project.compiled_contracts) == compiled_contracts_object_id
