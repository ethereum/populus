import sys
import os
from click.testing import CliRunner

from populus.project import Project
from populus.utils.filesystem import (
    get_migrations_dir,
)

from populus.cli import main


def test_makemigration(project_dir, write_project_file):
    runner = CliRunner()

    write_project_file(
        "contracts/Simple.sol",
        "contract Simple { function Simple() {}}"
    )

    migrations_dir = get_migrations_dir(project_dir, lazy_create=False)

    assert not os.path.exists(migrations_dir)

    result = runner.invoke(main, ['makemigration'])
    assert result.exit_code == 0, result.output + str(result.exception)

    assert os.path.exists(migrations_dir)
    assert os.path.exists(os.path.join(migrations_dir, '0001_initial.py'))

    assert not os.path.exists(os.path.join(migrations_dir, '0002_auto.py'))

    result = runner.invoke(main, ['makemigration'])
    assert result.exit_code == 0, result.output + str(result.exception)

    assert os.path.exists(os.path.join(migrations_dir, '0002_auto.py'))
    assert not os.path.exists(os.path.join(migrations_dir, '0003_custom_name.py'))

    result = runner.invoke(main, ['makemigration', 'custom_name'])
    assert result.exit_code == 0, result.output + str(result.exception)

    assert os.path.exists(os.path.join(migrations_dir, '0003_custom_name.py'))

    project = Project()

    assert len(project.migrations) == 3

    m1, m2, m3 = project.migrations

    assert m1.migration_id == '0001_initial'
    assert m1.dependencies == []

    assert m2.migration_id == '0002_auto'
    assert m2.dependencies == ['0001_initial']

    assert m3.migration_id == '0003_custom_name'
    assert m3.dependencies == ['0002_auto']


def test_makemigration_works_with_no_contracts(project_dir):
    runner = CliRunner()

    result = runner.invoke(main, ['makemigration', 'my_first_migration'])
    assert result.exit_code == 0, result.output + str(result.exception)

    migrations_dir = get_migrations_dir(project_dir, lazy_create=False)
    assert os.path.exists(migrations_dir)
    assert os.path.exists(os.path.join(migrations_dir, '0001_my_first_migration.py'))

    project = Project()

    assert len(project.migrations) == 1

    m1 = project.migrations[0]

    assert m1.migration_id == '0001_initial'
    assert m1.dependencies == []
    assert m1.compiled_contracts == {}
