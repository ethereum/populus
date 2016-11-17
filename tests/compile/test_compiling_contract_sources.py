import pytest

from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.testing import (
    load_contract_fixture,
)


@load_contract_fixture('Math.sol')
def test_compiling_project_contracts(project):
    source_paths, contract_data = compile_project_contracts(
        project.project_dir,
        project.contracts_source_dir,
    )

    assert 'contracts/Math.sol' in source_paths

    assert 'Math' in contract_data
    assert 'bytecode' in contract_data['Math']
    assert 'bytecode_runtime' in contract_data['Math']
    assert 'abi' in contract_data['Math']
