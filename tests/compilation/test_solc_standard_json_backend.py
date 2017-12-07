import os

import pytest

from solc.main import (
    solc_supports_standard_json_interface,
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
    ('compilation.backend', {"$ref": "compilation.backends.SolcStandardJSON"}),
)


GREETER_SOURCE_PATH = os.path.join(ASSETS_DIR, 'Greeter.sol')


pytestmark = pytest.mark.skipif(
    not solc_supports_standard_json_interface(),
    reason="Solc compiler does not support standard json compilation",
)


#
# Normal project contracts
#
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


#
# Contracts in the `./tests` directory
#
@load_test_contract_fixture('TestMath.sol')
def test_compiling_with_test_contracts(project):
    source_paths, compiled_contracts = compile_project_contracts(project)

    assert 'TestMath' in compiled_contracts


#
# Abstract contracts
#
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


#
# Provided "Greeter" contract
#
@load_contract_fixture(GREETER_SOURCE_PATH)
def test_compiling_example_greeter_contract(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'Greeter' in compiled_contracts


#
# Import remappings
#
@load_contract_fixture('RemapImported.sol')
@load_contract_fixture('ImportRemappingTestA.sol')
@update_project_config(
    (
        'compilation.import_remappings',
        ['import-path-for-A=contracts'],
    ),
)
def test_compiling_with_local_import_remappings(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'ImportRemappingTestA' in compiled_contracts
    assert 'RemapImported' in compiled_contracts
    assert 'RemapImportedNotUsed' in compiled_contracts


@load_contract_fixture('RemapImported.sol', 'another-directory/contracts/RemapImported.sol')
@load_contract_fixture('ImportRemappingTestA.sol')
@update_project_config(
    (
        'compilation.import_remappings',
        ['import-path-for-A=another-directory/contracts'],
    ),
    (
        'compilation.backend',
        {
            'class': "populus.compilation.backends.SolcStandardJSONBackend",
            'settings': {
                'stdin': {
                    'optimizer': {'enabled': True, 'runs': 500},
                    'outputSelection': {
                        '*': {
                            '*': [
                                'abi',
                                'metadata',
                                'evm.bytecode.object',
                                'evm.bytecode.linkReferences',
                                'evm.deployedBytecode.object',
                                'evm.deployedBytecode.linkReferences',
                            ]
                        },
                    },
                },
                'command_line_options': {
                    'allow_paths': './another-directory/contracts',
                },
            },
        }
    ),
    (
        'compilation.contracts_source_dirs',
        ['./contracts', './another-directory/contracts'],
    ),
)
def test_compiling_with_import_remapping_outside_contracts_directory(project):
    _, compiled_contracts = compile_project_contracts(project)

    assert 'ImportRemappingTestA' in compiled_contracts
    assert 'RemapImported' in compiled_contracts
    assert 'RemapImportedNotUsed' in compiled_contracts
