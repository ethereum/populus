from populus.migrations import (
    run_migrations,
    Migration,
    DeployContract,
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

    run_migrations([TestMigration], web3, registrar)

    registrar.call().exists('contract/Math') is False
    math_address = registrar.call().getAddress('contract/Math')

    math = web3.eth.contract(address=math_address, **MATH)
    assert math.call().multiply7(3) == 21
