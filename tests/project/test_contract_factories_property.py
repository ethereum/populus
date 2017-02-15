import pytest

from populus.utils.testing import load_contract_fixture


@load_contract_fixture('Math.sol')
def test_project_contract_factories_property(project):
    MATH = project.compiled_contracts['Math']

    with project.get_chain('tester') as chain:
        assert len(chain.contract_factories.Math.abi) == len(MATH['abi'])
        assert len(chain.contract_factories.Math.bytecode) > 2
        assert len(chain.contract_factories.Math.bytecode_runtime) > 2
