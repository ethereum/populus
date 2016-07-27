from populus.deployment import (
    deploy_contracts,
)


def test_single_contract_deployment(web3, MATH):
    contracts = {'Math': MATH}
    deployed_contracts = deploy_contracts(web3, contracts, timeout=1)

    assert len(deployed_contracts) == 1

    Math = deployed_contracts['Math']
    assert web3.eth.getCode(Math.address) == MATH['code_runtime']


def test_multi_contract_deployment(web3, MATH, SIMPLE_CONSTRUCTOR):
    contracts = {
        'Math': MATH,
        'SimpleConstructor': SIMPLE_CONSTRUCTOR,
    }
    deployed_contracts = deploy_contracts(web3, contracts, timeout=1)

    assert len(deployed_contracts) == 2

    Math = deployed_contracts['Math']
    assert web3.eth.getCode(Math.address) == MATH['code_runtime']

    SimpleConstructor = deployed_contracts['SimpleConstructor']
    assert web3.eth.getCode(SimpleConstructor.address) == SIMPLE_CONSTRUCTOR['code_runtime']


def test_deployment_with_constructor_arguments(web3, WITH_CONSTRUCTOR_ARGUMENTS):
    contracts = {
        'WithConstructorArguments': WITH_CONSTRUCTOR_ARGUMENTS,
    }
    deployed_contracts = deploy_contracts(
        web3,
        contracts,
        constructor_args={
            'WithConstructorArguments': [1234, "abcd"],
        },
        timeout=1,
    )

    assert len(deployed_contracts) == 1

    WithConstructorArguments = deployed_contracts['WithConstructorArguments']
    assert web3.eth.getCode(WithConstructorArguments.address) == WITH_CONSTRUCTOR_ARGUMENTS['code_runtime']

    web3.eth.sendTransaction({'to': WithConstructorArguments.address, 'from': web3.eth.coinbase, 'value': 1})

    a = WithConstructorArguments.call().data_a()
    assert a == 1234

    b = WithConstructorArguments.call().data_b()
    assert b"abcd" in b
