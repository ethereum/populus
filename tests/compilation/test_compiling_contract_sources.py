from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.compile import (
    get_contracts_source_dir,
)
from populus.utils.testing import (
    load_contract_fixture,
    load_test_contract_fixture,
)


@load_contract_fixture('Math.sol')
def test_compiling_project_contracts(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'contracts/Math.sol' in source_paths

    assert 'Math' in contract_data
    assert 'bytecode' in contract_data['Math']
    assert 'bytecode_runtime' in contract_data['Math']
    assert 'abi' in contract_data['Math']


@load_contract_fixture('ImportTestA.sol')
@load_contract_fixture('ImportTestB.sol')
@load_contract_fixture('ImportTestC.sol')
def test_compiling_with_local_project_imports(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'ImportTestA' in contract_data
    assert 'ImportTestB' in contract_data
    assert 'ImportTestC' in contract_data


@load_test_contract_fixture('TestMath.sol')
def test_compiling_with_test_contracts(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'TestMath' in contract_data
