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


def test_project_compiled_contracts_auto_update(project_dir,
                                                write_project_file, MATH,
                                                SIMPLE_CONSTRUCTOR):
    write_project_file('contracts/Math.sol', MATH['source'])

    project = Project()

    assert 'Math' in project.compiled_contracts
    assert 'WithNoArgumentConstructor' not in project.compiled_contracts

    compiled_contracts_object_id = id(project.compiled_contracts)

    write_project_file('contracts/WithNoArgumentConstructor.sol', SIMPLE_CONSTRUCTOR['source'])

    compiled_contracts_object_id != id(project.compiled_contracts)

    assert 'Math' in project.compiled_contracts
    assert 'WithNoArgumentConstructor' in project.compiled_contracts
