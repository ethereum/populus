import os
import pytest
from click.testing import CliRunner

from populus.utils.contracts import (
    get_contracts_source_dir,
)

from populus.cli import main




def test_initializing_project(project_dir):
    contracts_source_dir = get_contracts_source_dir(project_dir)

    os.rmdir(contracts_source_dir)

    expected_paths = (
        contracts_source_dir,
        os.path.join(contracts_source_dir, 'Greeter.sol'),
        os.path.join(project_dir, 'tests'),
        os.path.join(project_dir, 'tests', 'test_greeter.py'),
    )

    for path in expected_paths:
        assert not os.path.exists(path)

    runner = CliRunner()
    result = runner.invoke(main, ['init'])

    assert result.exit_code == 0, result.output + str(result.exception)

    for path in expected_paths:
        assert os.path.exists(path)
