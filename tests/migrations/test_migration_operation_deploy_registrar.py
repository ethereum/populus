from populus.migrations.registrar import (
    get_registrar,
)
from populus.migrations import (
    DeployRegistrar,
)


def test_deploy_registrar_operation(web3, chain):
    registrar_deploy_txn = DeployRegistrar().execute(chain=chain)['deploy-transaction-hash']
    registrar_address = chain.wait.for_contract_address(registrar_deploy_txn, timeout=30)

    assert registrar_address

    registrar = get_registrar(web3, registrar_address)

    assert registrar
