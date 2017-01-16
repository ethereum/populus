import pytest

from populus.utils.chains import (
    get_chain_definition,
)
from populus.packages.build import (
    construct_deployments_object,
)


TEST_CONTRACT_SOURCE = """pragma solidity ^0.4.0;

contract TestContract {
    uint value;

    function readValue() constant returns (uint) {
        return value;
    }

    function setValue(uint _value) public {
        value = _value;
    }
}
"""


@pytest.fixture()
def TestContract(project_dir, write_project_file):
    write_project_file('contracts/TestContract.sol', TEST_CONTRACT_SOURCE)


def test_construct_deployments_object(project, TestContract):
    contract_data = project.compiled_contract_data['TestContract']

    with project.get_chain('tester') as chain:
        provider = chain.store.provider
        test_contract, created = provider.get_or_deploy_contract('TestContract')
        assert created

        deployments_object = construct_deployments_object(provider, ['TestContract'])

    assert 'TestContract' in deployments_object

    deployed_instance = deployments_object['TestContract']
    assert deployed_instance['runtime_bytecode'] == contract_data['code_runtime']
    assert deployed_instance['address'] == test_contract.address
    assert deployed_instance['contract_type'] == 'TestContract'
