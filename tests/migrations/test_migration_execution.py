from populus.migrations import (
    Migration,
    SendTransaction,
    DeployContract,
    RunPython,
    TransactContract,
    DeployRegistrar,
)


def test_single_migration_execution(web3, MATH, registrar):
    class TestMigration(Migration):
        migration_id = '0001_initial'
        dependencies = []

        operations = [
            DeployContract('Math'),
        ]

        compiled_contracts = {
            'Math': {
                'code': MATH['code'],
                'code_runtime': MATH['code_runtime'],
                'abi': MATH['abi'],
            },
        }

    migration = TestMigration(web3, registrar.address)
    migration.execute()

    registrar.call().exists('contract/Math') is False
    math_address = registrar.call().getAddress('contract/Math')

    math = web3.eth.contract(address=address, **MATH)
