import pytest

from populus.project import Project


def test_project_compiled_contracts_with_no_default_env(project_dir,
                                                        write_project_file,
                                                        MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    project = Project()

    assert 'Math' in project.compiled_contracts
    assert 'bytecode' in project.compiled_contracts['Math']
    assert 'bytecode_runtime' in project.compiled_contracts['Math']
    assert 'abi' in project.compiled_contracts['Math']

    compiled_contracts_object_id = id(project.compiled_contracts)

    assert id(project.compiled_contracts) == compiled_contracts_object_id


def test_project_fill_contracts_cache(write_project_file,
                                      MATH):
    write_project_file('contracts/Math.sol', MATH['source'])
    source_mtime = Project().get_source_modification_time()

    project = Project()
    compiled_contracts_object_id = id(project.compiled_contracts)

    # fill with code from the future -> no recompilation
    project.fill_contracts_cache(project.compiled_contracts, source_mtime + 10)
    assert id(project.compiled_contracts) == compiled_contracts_object_id

    # fill with code from the past -> recompilation
    project.fill_contracts_cache(project.compiled_contracts, source_mtime - 10)
    assert not id(project.compiled_contracts) == compiled_contracts_object_id
