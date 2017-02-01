import os
import pytest
from click.testing import CliRunner

from populus.utils.filesystem import (
    get_contracts_dir,
)

from populus.cli import main


def test_initializing_empty_project(project_dir):
    contracts_dir = get_contracts_dir(project_dir)

    os.rmdir(contracts_dir)

    expected_paths = (
        os.path.join(project_dir, 'populus.json'),
        contracts_dir,
        os.path.join(contracts_dir, 'Greeter.sol'),
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


def test_initializing_with_legacy_ini_config(project_dir, write_project_file):
    default_contracts_dir = get_contracts_dir(project_dir)
    os.rmdir(default_contracts_dir)

    write_project_file('populus.ini', "[populus]\ncontracts_dir=./custom-contracts-dir")

    contracts_dir = os.path.join(project_dir, 'custom-contracts-dir')

    expected_paths = (
        os.path.join(project_dir, 'populus.json'),
        contracts_dir,
        os.path.join(contracts_dir, 'Greeter.sol'),
        os.path.join(project_dir, 'tests'),
        os.path.join(project_dir, 'tests', 'test_greeter.py'),
    )

    for path in expected_paths:
        assert not os.path.exists(path)

    runner = CliRunner()
    result = runner.invoke(main, ['init'], input='\n')

    assert result.exit_code == 0, result.output + str(result.exception)

    for path in expected_paths:
        assert os.path.exists(path), result.output
