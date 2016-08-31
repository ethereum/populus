import os
import pytest
from click.testing import CliRunner

from populus.utils.filesystem import (
    get_contracts_dir,
)

from populus.cli import main




def test_initializing_project(project_dir):
    contracts_dir = get_contracts_dir(project_dir)

    os.rmdir(contracts_dir)

    expected_paths = (
        contracts_dir,
        os.path.join(contracts_dir, 'Greeter.sol'),
        os.path.join(project_dir, 'tests'),
        os.path.join(project_dir, 'tests', 'test_greeter.py'),
        os.path.join(project_dir, 'populus.ini')
    )

    for path in expected_paths:
        assert not os.path.exists(path)

    runner = CliRunner()
    result = runner.invoke(main, ['init'])

    assert result.exit_code == 0, result.output + str(result.exception)

    for path in expected_paths:
        assert os.path.exists(path)
