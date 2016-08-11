from populus.utils.transactions import (
    get_contract_address_from_txn,
)
from populus.migrations.registrar import (
    get_compiled_registrar_contract,
)
from populus.migrations import (
    DeployRegistrar,
)


def test_deploy_registrar_operation(web3, chain):
    registrar_deploy_txn = DeployRegistrar().execute(chain=chain)['deploy-transaction-hash']
    registrar_address = get_contract_address_from_txn(web3, registrar_deploy_txn, timeout=30)

    assert registrar_address

    registrar = get_compiled_registrar_contract(web3, registrar_address)

    assert registrar
