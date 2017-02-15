import pytest

from populus import Project

from populus.utils.testing import load_contract_fixture


@load_contract_fixture('Math.sol')
def test_project_compiled_contracts_with_no_default_env(project):
    assert 'Math' in project.compiled_contracts
    assert 'bytecode' in project.compiled_contracts['Math']
    assert 'bytecode_runtime' in project.compiled_contracts['Math']
    assert 'abi' in project.compiled_contracts['Math']

    compiled_contracts_object_id = id(project.compiled_contracts)

    assert id(project.compiled_contracts) == compiled_contracts_object_id


@load_contract_fixture('Math.sol')
def test_project_fill_contracts_cache(project):
    source_mtime = project.get_source_modification_time()

    compiled_contracts_object_id = id(project.compiled_contracts)

    # fill with code from the future -> no recompilation
    project.fill_contracts_cache(project.compiled_contracts, source_mtime + 10)
    assert id(project.compiled_contracts) == compiled_contracts_object_id

    # fill with code from the past -> recompilation
    project.fill_contracts_cache(project.compiled_contracts, source_mtime - 10)
    assert not id(project.compiled_contracts) == compiled_contracts_object_id
