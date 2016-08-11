from populus.migrations import (
    run_migrations,
    Migration,
    DeployContract,
)


def test_single_migration_execution(web3, chain, MATH):
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

    run_migrations([TestMigration], chain)

    assert chain.registrar.call().exists('contract/Math') is True
    math_address = chain.registrar.call().getAddress('contract/Math')

    math = web3.eth.contract(address=math_address, **MATH)
    assert math.call().multiply7(3) == 21
