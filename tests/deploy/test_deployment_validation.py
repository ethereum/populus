import pytest

from populus.deployment import (
    deploy_contracts,
    validate_deployed_contracts,
)


def test_validation_fails_if_no_code(web3, MATH):
    contracts = {'Math': MATH}
    deployed_contracts = deploy_contracts(web3, contracts, max_wait=1, txn_defaults={'gas': 1})

    deployed_contracts.Math.address = "0xd3cda913deb6f67967b99d67acdfa1712c293601"

    with pytest.raises(ValueError):
        validate_deployed_contracts(web3, deployed_contracts)
