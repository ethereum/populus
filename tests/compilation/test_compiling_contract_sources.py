import os

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

GREETER_SOURCE_PATH = os.path.join(ASSETS_DIR, 'Greeter.sol')


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
@load_contract_fixture('ImportTestD.sol')
@load_contract_fixture('ImportTestE.sol')
@load_contract_fixture('ImportTestF.sol')
def test_compiling_with_local_project_imports(project):
    _, contract_data = compile_project_contracts(project)

    assert 'ImportTestA' in contract_data
    assert 'ImportTestB' in contract_data
    assert 'ImportTestC' in contract_data
    assert 'ImportTestD' in contract_data
    assert 'ImportTestE' in contract_data
    assert 'ImportTestF' in contract_data
    
    assert 'ImportTestRemapA' in contract_data
    assert 'ImportTestRemapB' in contract_data
    assert 'ImportTestRemapC' in contract_data
    assert 'ImportTestRemapD' in contract_data #side effect
    assert 'ImportTestRemapE' in contract_data


@load_test_contract_fixture('TestMath.sol')
def test_compiling_with_test_contracts(project):
    source_paths, contract_data = compile_project_contracts(project)

    assert 'TestMath' in contract_data


@load_contract_fixture('Abstract.sol')
def test_compiling_with_abstract_contract(project):
    _, contract_data = compile_project_contracts(project)

    assert 'Abstract' in contract_data


@load_contract_fixture('Abstract.sol')
@load_contract_fixture('UsesAbstract.sol')
def test_compiling_with_abstract_contract_inhereted(project):
    _, contract_data = compile_project_contracts(project)

    assert 'Abstract' in contract_data
    assert 'UsesAbstract' in contract_data


@load_contract_fixture(GREETER_SOURCE_PATH)
def test_compiling_example_greeter_contract(project):
    _, contract_data = compile_project_contracts(project)

    assert 'Greeter' in contract_data
