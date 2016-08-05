from populus.utils.string import (
    force_text,
)
from populus.migrations import (
    Migration,
    SendTransaction,
    DeployContract,
    RunPython,
    TransactContract,
)


def test_migration_execution(web3, MATH, registrar):
    class TestMigration(Migration):
        migration_id = '0001_initial'
        dependencies = []

        operations = [
            DeployContract('Math'),
        ]

        compiled_contracts = {
            'Math': MATH,
        }

    assert registrar.call().exists('migration/0001_initial') is False

    TestMigration().execute(web3, registrar.address)

    assert registrar.call().exists('migration/0001_initial') is True
    assert registrar.call().getBool('migration/0001_initial') is True

    assert registrar.call().exists('migration/0001_initial/operation/0') is True

    deploy_txn_hash_bytes = registrar.call().get('migration/0001_initial/operation/0')
    deploy_txn_hash = web3.fromAscii(deploy_txn_hash_bytes)
    deploy_txn_receipt = web3.eth.getTransactionReceipt(deploy_txn_hash)

    contract_address = deploy_txn_receipt['contractAddress']
    assert contract_address

    contract_code = web3.eth.getCode(contract_address)

    assert force_text(contract_code) == force_text(MATH['code_runtime'])
