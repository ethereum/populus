import pytest

from populus.packages.build import (
    construct_deployments_object,
)

from populus.utils.chains import (
    get_chain_definition,
)
from populus.utils.testing import (
    load_contract_fixture,
    load_example_package,
)


@load_contract_fixture('Math.sol')
def test_construct_deployments_object_with_project_contract_deployment(project):
    contract_data = project.compiled_contract_data['Math']

    with project.get_chain('tester') as chain:
        provider = chain.provider
        test_contract, created = provider.get_or_deploy_contract('Math')
        assert created

        deployments_object = construct_deployments_object(provider, ['Math'])

    assert 'Math' in deployments_object

    deployed_instance = deployments_object['Math']
    assert deployed_instance['runtime_bytecode'] == contract_data['bytecode_runtime']
    assert deployed_instance['address'] == test_contract.address
    assert deployed_instance['contract_type'] == 'Math'


@load_example_package('standard-token')
def test_construct_deployments_object_using_dependency_contract_type(project):
    contract_data = project.compiled_contract_data['StandardToken']

    with project.get_chain('tester') as chain:
        provider = chain.provider
        test_contract, created = provider.get_or_deploy_contract(
            'StandardToken',
            deploy_args=(1000000,),
        )
        assert created

        deployments_object = construct_deployments_object(provider, ['StandardToken'])

    assert 'StandardToken' in deployments_object

    deployed_instance = deployments_object['StandardToken']
    assert deployed_instance['runtime_bytecode'] == contract_data['bytecode_runtime']
    assert deployed_instance['address'] == test_contract.address
    assert deployed_instance['contract_type'] == 'standard-token:StandardToken'


@load_example_package('safe-math-lib')
@load_contract_fixture('UsesSafeMathLib.sol')
def test_construct_deployments_object_using_dependency_link_value(project):
    contract_data = project.compiled_contract_data['UsesSafeMathLib']

    with project.get_chain('tester') as chain:
        provider = chain.provider
        test_contract, created = provider.get_or_deploy_contract('UsesSafeMathLib')
        assert created

        deployments_object = construct_deployments_object(provider, ['UsesSafeMathLib'])

    assert 'UsesSafeMathLib' in deployments_object

    deployed_instance = deployments_object['UsesSafeMathLib']
    assert deployed_instance['runtime_bytecode'] == contract_data['bytecode_runtime']
    assert deployed_instance['address'] == test_contract.address
    assert deployed_instance['contract_type'] == 'UsesSafeMathLib'

    link_dependencies = deployed_instance['link_dependencies']
    assert len(link_dependencies) == 1
    link_value = link_dependencies[0]
    assert link_value['value'] == 'safe-math-lib:SafeMathLib'
