import pytest

from populus import Project

from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.contracts import (
    get_contracts_source_dir,
)


def test_compiling_project_contracts(project_dir, write_project_file, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    project = Project()

    source_paths, contract_data = compile_project_contracts(project)

    assert 'contracts/Math.sol' in source_paths

    assert 'Math' in contract_data
    assert 'code' in contract_data['Math']
    assert 'code_runtime' in contract_data['Math']
    assert 'abi' in contract_data['Math']
