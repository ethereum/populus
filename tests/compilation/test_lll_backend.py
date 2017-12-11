import pytest

from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.testing import (
    load_contract_fixture,
    update_project_config,
)

@load_contract_fixture('Greeter.lll')
@load_contract_fixture('Greeter.lll.abi')
@update_project_config(
    (
        'compilation.backend.class',
        'populus.compilation.backends.LLLBackend',
    ),
)
def test_compiling_lll_project_contracts(project):
    source_paths, compiled_contracts = compile_project_contracts(project)

    assert 'contracts/Greeter.lll' in source_paths

    assert 'Greeter' in compiled_contracts
    contract_data = compiled_contracts['Greeter']
    assert 'bytecode' in contract_data
    assert 'bytecode_runtime' in contract_data
    assert 'abi' in contract_data
    function_names = [x['name'] for x in contract_data['abi'] if x['type'] != 'constructor']
    assert 'setGreeting' in function_names
    assert 'greet' in function_names
