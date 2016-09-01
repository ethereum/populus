from populus.migrations import (
    Migration,
    DeployContract,
)
from populus.migrations.writer import (
    write_migration,
)
from populus.migrations.migration import (
    get_migration_classes_for_execution,
)


def test_migrated_chain_fixture(project_dir, write_project_file, request,
                                MATH):
    write_project_file('contracts/Math.sol', MATH['source'])
    write_project_file('migrations/__init__.py')

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

    with open('migrations/0001_initial.py', 'w') as migration_file:
        write_migration(migration_file, TestMigration)

    project = request.getfuncargvalue('project')
    assert len(project.migrations) == 1

    chain = request.getfuncargvalue('chain')

    registrar = chain.registrar
    assert not registrar.call().exists('contract/Math')

    migrated_chain = request.getfuncargvalue('migrated_chain')

    assert registrar.call().exists('contract/Math')
