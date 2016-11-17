import pytest

from populus.project import Project


def test_project_compiled_contracts_with_no_default_env(project_dir,
                                                        write_project_file,
                                                        MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    project = Project()

    assert 'Math' in project.compiled_contract_data
    assert 'code' in project.compiled_contract_data['Math']
    assert 'code_runtime' in project.compiled_contract_data['Math']
    assert 'abi' in project.compiled_contract_data['Math']

    compiled_contracts_object_id = id(project.compiled_contract_data)

    assert id(project.compiled_contract_data) == compiled_contracts_object_id


def test_project_fill_contracts_cache(write_project_file,
                                      MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    project = Project()
    source_mtime = project.get_source_modification_time()

    compiled_contracts_object_id = id(project.compiled_contract_data)

    # fill with code from the future -> no recompilation
    project.fill_contracts_cache(project.compiled_contract_data, source_mtime + 10)
    assert id(project.compiled_contract_data) == compiled_contracts_object_id

    # fill with code from the past -> recompilation
    project.fill_contracts_cache(project.compiled_contract_data, source_mtime - 10)
    assert not id(project.compiled_contract_data) == compiled_contracts_object_id
