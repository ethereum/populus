import os

import pytest

from semantic_version import (
    Spec,
)

from solc import (
    get_solc_version,
)

from populus import ASSETS_DIR

from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.testing import (
    load_contract_fixture,
    load_test_contract_fixture,
    update_project_config,
)


_populus_config_key_value_pairs = (
    ('compilation.backend', {"$ref": "compilation.backends.SolcCombinedJSON"}),
)


GREETER_SOURCE_PATH = os.path.join(ASSETS_DIR, 'Greeter.sol')


pytestmark = pytest.mark.skipif(
    not get_solc_version() in Spec('<=0.4.8'),
    reason="Solc compiler not supported for combined json compilation",
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


@load_contract_fixture('ImportTestA.sol')
@load_contract_fixture('ImportTestB.sol')
@load_contract_fixture('ImportTestC.sol')
def test_compiling_with_local_project_imports(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'ImportTestA' in compiled_contracts
    assert 'ImportTestB' in compiled_contracts
    assert 'ImportTestC' in compiled_contracts


@load_contract_fixture('RemapImported.sol')
@load_contract_fixture('ImportRemappingTestA.sol')
@update_project_config(
    ('compilation.import_remappings', [
        'import-path-for-A=contracts'
        ]),
)
def test_compiling_with_import_remappings(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'ImportRemappingTestA' in compiled_contracts
    assert 'RemapImported' in compiled_contracts
    assert 'RemapImportedNotUsed' in compiled_contracts


@load_test_contract_fixture('TestMath.sol')
def test_compiling_with_test_contracts(project):
    source_paths, compiled_contracts = compile_project_contracts(project)

    assert 'TestMath' in compiled_contracts


@load_contract_fixture('Abstract.sol')
def test_compiling_with_abstract_contract(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Abstract' in compiled_contracts


@load_contract_fixture('Abstract.sol')
@load_contract_fixture('UsesAbstract.sol')
def test_compiling_with_abstract_contract_inhereted(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Abstract' in compiled_contracts
    assert 'UsesAbstract' in compiled_contracts


@load_contract_fixture(GREETER_SOURCE_PATH)
def test_compiling_example_greeter_contract(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Greeter' in compiled_contracts


@load_contract_fixture('Library13.sol')
@load_contract_fixture('Multiply13.sol')
def test_link_reference_extraction_from_bytecode(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Library13' in compiled_contracts
    assert 'Multiply13' in compiled_contracts

    assert 'Library13' in compiled_contracts['Multiply13']['direct_dependencies']


@load_contract_fixture('Library13.sol', 'contracts/long-path-to-truncate-linkref-placeholders/Library13.sol')
@load_contract_fixture('Multiply13.sol', 'contracts/long-path-to-truncate-linkref-placeholders/Multiply13.sol')
def test_detects_contract_name_truncation_from_long_file_paths(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Library13' in compiled_contracts
    assert 'Multiply13' in compiled_contracts

    assert 'Library13' in compiled_contracts['Multiply13']['direct_dependencies']
