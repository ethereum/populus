from populus.deployment import (
    deploy_contracts,
)


def test_single_contract_deployment(web3, MATH):
    contracts = {'Math': MATH}
    deployed_contracts = deploy_contracts(web3, contracts)

    assert len(deployed_contracts) == 1

    Math = deployed_contracts['Math']
    assert web3.eth.getCode(Math.address) == MATH['code']
