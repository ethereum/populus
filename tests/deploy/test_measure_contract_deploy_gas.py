from populus.deployment import (
    measure_contract_deploy_gas,
)


def test_measuring_deploy_gas_on_successful_deploy(Math):
    gas_provided, gas_used = measure_contract_deploy_gas(Math)

    expected_gas = 168511

    assert abs(gas_used - expected_gas) < 100
