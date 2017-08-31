import os

import pytest

from solc.main import (
    solc_supports_standard_json_interface,
)

from populus import ASSETS_DIR


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
    source_paths, compiled_contracts = project.compile_project()

    os.path.join(project.project_root_dir, 'contracts/Math.sol') in source_paths

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
    _, compiled_contracts = project.compile_project()

    assert 'ImportTestA' in compiled_contracts
    assert 'ImportTestB' in compiled_contracts
    assert 'ImportTestC' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_test_contract_fixture('TestMath.sol')
def test_compiling_with_test_contracts(project):
    source_paths, compiled_contracts = project.compile_project()

    assert 'TestMath' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_contract_fixture('Abstract.sol')
def test_compiling_with_abstract_contract(project):
    _, compiled_contracts = project.compile_project()

    assert 'Abstract' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
@load_contract_fixture('Abstract.sol')
@load_contract_fixture('UsesAbstract.sol')
def test_compiling_with_abstract_contract_inhereted(project):
    _, compiled_contracts = project.compile_project()

    assert 'Abstract' in compiled_contracts
    assert 'UsesAbstract' in compiled_contracts


@pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)
def test_compiling_example_greeter_contract(project):
    _, compiled_contracts = project.compile_project()

    assert 'Greeter' in compiled_contracts
