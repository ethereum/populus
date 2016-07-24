from populus.deployment import (
    deploy_contracts,
)


def test_single_contract_deployment(web3, MATH):
    contracts = {'Math': MATH}
    deployed_contracts = deploy_contracts(web3, contracts, max_wait=1)

    assert len(deployed_contracts) == 1

    Math = deployed_contracts['Math']
    assert web3.eth.getCode(Math.address) == MATH['code_runtime']


def test_multi_contract_deployment(web3, MATH, SIMPLE_CONSTRUCTOR):
    contracts = {
        'Math': MATH,
        'SimpleConstructor': SIMPLE_CONSTRUCTOR,
    }
    deployed_contracts = deploy_contracts(web3, contracts, max_wait=1)

    assert len(deployed_contracts) == 2

    Math = deployed_contracts['Math']
    assert web3.eth.getCode(Math.address) == MATH['code_runtime']

    SimpleConstructor = deployed_contracts['SimpleConstructor']
    assert web3.eth.getCode(SimpleConstructor.address) == SIMPLE_CONSTRUCTOR['code_runtime']


def test_deployment_with_constructor_arguments(web3, WITH_CONSTRUCTOR_ARGUMENT):
    contracts = {
        'WithConstructorArguments': WITH_CONSTRUCTOR_ARGUMENT,
    }
    deployed_contracts = deploy_contracts(
        web3,
        contracts,
        constructor_args={
            'SimpleConstructor':
        },
        max_wait=1)

    assert len(deployed_contracts) == 1

    Math = deployed_contracts['Math']
    assert web3.eth.getCode(Math.address) == MATH['code_runtime']

    Emitter = deployed_contracts['Emitter']
    assert web3.eth.getCode(Emitter.address) == EMITTER['code_runtime']
