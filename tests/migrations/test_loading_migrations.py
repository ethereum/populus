import os

from populus.utils.filesystem import (
    get_migrations_dir,
)
from populus.migrations import (
    Migration,
)
from populus.migrations.loading import (
    load_project_migrations,
)
from populus.migrations.writer import (
    write_migration,
)


def test_load_project_migrations(project_dir, MATH):
    migrations_dir = get_migrations_dir(project_dir)
    migration_0001_file_path = os.path.join(migrations_dir, '0001_initial.py')
    migration_0002_file_path = os.path.join(migrations_dir, '0002_the_second_migration.py')
    migration_0003_file_path = os.path.join(migrations_dir, '0003_the_third_migration.py')

    class MigrationA(Migration):
        migration_id = '0001_initial'
        dependencies = []
        operations = []
        compiled_contracts = {
            'Math': MATH,
        }

    class MigrationB(Migration):
        migration_id = '0002_the_second_migration'
        dependencies = ['0001_initial']
        operations = []
        compiled_contracts = {
            'Math': MATH,
        }

    class MigrationC(Migration):
        migration_id = '0003_the_third_migration'
        dependencies = ['0002_the_second_migration']
        operations = []
        compiled_contracts = {
            'Math': MATH,
        }

    with open(migration_0001_file_path, 'w') as migration_0001_file:
        write_migration(migration_0001_file, MigrationA)

    with open(migration_0002_file_path, 'w') as migration_0002_file:
        write_migration(migration_0002_file, MigrationB)

    with open(migration_0003_file_path, 'w') as migration_0003_file:
        write_migration(migration_0003_file, MigrationC)

    migration_classes = load_project_migrations(project_dir)

    assert len(migration_classes) == 3
    actual_ids = {m.migration_id for m in migration_classes}

    expected_ids = {'0001_initial', '0002_the_second_migration', '0003_the_third_migration'}

    assert actual_ids == expected_ids
