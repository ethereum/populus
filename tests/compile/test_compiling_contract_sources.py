import pytest

from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.filesystem import (
    get_contracts_dir,
)


def test_compiling_project_contracts(project_dir, write_project_file, MATH):
    write_project_file('contracts/Math.sol', MATH['source'])

    source_paths, contract_data = compile_project_contracts(
        project_dir,
        get_contracts_dir(project_dir),
    )

    assert 'contracts/Math.sol' in source_paths

    assert 'Math' in contract_data
    assert 'bytecode' in contract_data['Math']
    assert 'bytecode_runtime' in contract_data['Math']
    assert 'abi' in contract_data['Math']
