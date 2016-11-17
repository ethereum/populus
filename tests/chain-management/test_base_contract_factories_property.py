from populus.utils.testing import load_contract_fixture


@load_contract_fixture('Math.sol')
def test_chain_base_contract_factories_property(project):
    MATH = project.compiled_contract_data['Math']

    with project.get_chain('testrpc') as chain:
        assert len(chain.base_contract_factories.Math.abi) == len(MATH['abi'])
        assert len(chain.base_contract_factories.Math.bytecode) > 2
        assert len(chain.base_contract_factories.Math.bytecode_runtime) > 2
