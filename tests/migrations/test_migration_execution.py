from populus.migrations import (
    Migration,
    DeployContract,
)
from populus.migrations.migration import (
    get_migration_classes_for_execution,
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
                'bytecode': MATH['bytecode'],
                'bytecode_runtime': MATH['bytecode_runtime'],
                'abi': MATH['abi'],
            },
        }

    migrations_to_run = get_migration_classes_for_execution([TestMigration], chain)
    for migration in migrations_to_run:
        migration.execute()

    assert chain.registrar.call().exists('contract/Math') is True
    math_address = chain.registrar.call().getAddress('contract/Math')

    math = web3.eth.contract(address=math_address, **MATH)
    assert math.call().multiply7(3) == 21
