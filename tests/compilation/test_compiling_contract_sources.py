from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.compile import (
    get_contracts_source_dir,
)
from populus.utils.testing import (
    load_contract_fixture,
    load_test_contract_fixture,
    load_example_package,
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


@load_example_package('owned')
def test_compiling_with_single_installed_package(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'owned' in contract_data


@load_example_package('owned')
@load_example_package('standard-token')
def test_compiling_with_multiple_installed_packages(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'owned' in contract_data
    assert 'Token' in contract_data
    assert 'StandardToken' in contract_data


@load_example_package('transferable')
def test_compiling_with_nested_installed_packages(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'owned' in contract_data
    assert 'transferable' in contract_data


@load_example_package('transferable')
def test_compiling_with_nested_installed_packages(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'owned' in contract_data
    assert 'transferable' in contract_data


@load_test_contract_fixture('TestMath.sol')
def test_compiling_with_test_contracts(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'TestMath' in contract_data


@load_example_package('owned')
@load_test_contract_fixture('UsesOwned.sol')
def test_compiling_with_import_from_package(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'UsesOwned' in contract_data
    assert 'owned' in contract_data
