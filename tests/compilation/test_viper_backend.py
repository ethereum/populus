
import pytest


from populus.compilation import (
    compile_project_contracts,
)

from populus.utils.testing import (
    load_contract_fixture,
    update_project_config,
    viper_installed
)


pytestmark = pytest.mark.skipif(
    not viper_installed(),
    reason="Viper compiler not installed",
)


@load_contract_fixture('Greeter.v.py')
def test_compiling_viper_project_contracts(project):
    project.config['compilation']['backend'] = {
        'class': 'populus.compilation.backends.ViperBackend',
    }
    source_paths, compiled_contracts = compile_project_contracts(project)

    assert 'contracts/Greeter.v.py' in source_paths

    assert 'Greeter' in compiled_contracts
    contract_data = compiled_contracts['Greeter']
    assert 'bytecode' in contract_data
    assert 'bytecode_runtime' in contract_data
    assert 'abi' in contract_data
