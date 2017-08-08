import os

import pytest

from solc.main import (
    solc_supports_standard_json_interface,
)

from populus import ASSETS_DIR

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


_populus_config_key_value_pairs = (
    ('compilation.backend', {"$ref": "compilation.backends.SolcStandardJSON"}),
)


GREETER_SOURCE_PATH = os.path.join(ASSETS_DIR, 'Greeter.sol')


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_contract_fixture('Math.sol')
def test_compiling_project_contracts(project):
    source_paths, compiled_contracts = compile_project_contracts(project)

    assert 'contracts/Math.sol' in source_paths

    assert 'Math' in compiled_contracts
    contract_data = compiled_contracts['Math']
    assert 'bytecode' in contract_data
    assert 'bytecode_runtime' in contract_data
    assert 'abi' in contract_data


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_contract_fixture('ImportTestA.sol')
@load_contract_fixture('ImportTestB.sol')
@load_contract_fixture('ImportTestC.sol')
def test_compiling_with_local_project_imports(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'ImportTestA' in compiled_contracts
    assert 'ImportTestB' in compiled_contracts
    assert 'ImportTestC' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_test_contract_fixture('TestMath.sol')
def test_compiling_with_test_contracts(project):
    source_paths, compiled_contracts = compile_project_contracts(project)

    assert 'TestMath' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_contract_fixture('Abstract.sol')
def test_compiling_with_abstract_contract(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Abstract' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_contract_fixture('Abstract.sol')
@load_contract_fixture('UsesAbstract.sol')
def test_compiling_with_abstract_contract_inhereted(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Abstract' in compiled_contracts
    assert 'UsesAbstract' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_contract_fixture(GREETER_SOURCE_PATH)
def test_compiling_example_greeter_contract(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Greeter' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_example_package('owned')
def test_compiling_with_single_installed_package(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'owned' in contract_data


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_example_package('owned')
@load_example_package('standard-token')
def test_compiling_with_multiple_installed_packages(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'owned' in contract_data
    assert 'Token' in contract_data
    assert 'StandardToken' in contract_data


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_example_package('transferable')
def test_compiling_with_nested_installed_packages(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'owned' in contract_data
    assert 'transferable' in contract_data


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_example_package('transferable')
def test_compiling_with_nested_installed_packages(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'owned' in contract_data
    assert 'transferable' in contract_data


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_example_package('owned')
@load_test_contract_fixture('UsesOwned.sol')
def test_compiling_with_import_from_package(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'UsesOwned' in contract_data
    assert 'owned' in contract_data
