import os
import pytest
from click.testing import CliRunner

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

    result = runner.invoke(main, ['makemigration', '--empty'])
    assert result.exit_code == 0, result.output + str(result.exception)

    assert os.path.exists(migrations_dir)
    assert os.path.exists(os.path.join(migrations_dir, '0001_initial.py'))

    assert not os.path.exists(os.path.join(migrations_dir, '0002_auto.py'))

    result = runner.invoke(main, ['makemigration', '--empty'])
    assert result.exit_code == 0, result.output + str(result.exception)

    assert os.path.exists(os.path.join(migrations_dir, '0002_auto.py'))
    assert not os.path.exists(os.path.join(migrations_dir, '0003_custom_name.py'))

    result = runner.invoke(main, ['makemigration', '--empty', 'custom_name'])
    assert result.exit_code == 0, result.output + str(result.exception)

    assert os.path.exists(os.path.join(migrations_dir, '0003_custom_name.py'))
