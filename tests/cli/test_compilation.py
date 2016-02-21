import os
import pytest
import click
from click.testing import CliRunner

from populus.cli import main
from populus.solidity import is_solc_available

skip_if_no_sol_compiler = pytest.mark.skipif(
    not is_solc_available(),
    reason="'solc' compiler not available",
)

this_dir = os.path.dirname(__file__)


@skip_if_no_sol_compiler
def test_compiling(monkeypatch):
    monkeypatch.chdir(os.path.join(this_dir, 'projects/test-01/'))
    runner = CliRunner()
    result = runner.invoke(main, ['compile'])

    assert result.exit_code == 0, result.output
    assert 'owned.sol' in result.output
    assert 'mortal.sol' in result.output
    assert 'Mortal' in result.output
    assert 'Immortal' in result.output
    assert 'tests/cli/projects/test-01' in result.output


@skip_if_no_sol_compiler
def test_compiling_with_specified_contract(monkeypatch):
    monkeypatch.chdir(os.path.join(this_dir, 'projects/test-01/'))
    runner = CliRunner()
    result = runner.invoke(main, ['compile', 'Mortal'])

    assert result.exit_code == 0, result.output
    assert 'owned.sol' in result.output
    assert 'mortal.sol' in result.output
    assert 'Mortal' in result.output
    assert 'Immortal' not in result.output
    assert 'tests/cli/projects/test-01' in result.output


@skip_if_no_sol_compiler
@pytest.mark.parametrize('path', ('owned.sol', 'contracts/owned.sol'))
def test_compiling_with_specified_file(monkeypatch, path):
    monkeypatch.chdir(os.path.join(this_dir, 'projects/test-01/'))
    runner = CliRunner()
    result = runner.invoke(main, ['compile', path])

    assert result.exit_code == 0, result.output
    assert 'owned.sol' in result.output
    assert 'mortal.sol' in result.output
    assert 'Mortal' not in result.output
    assert 'Immortal' not in result.output
    assert ' owned\n' in result.output
    assert 'tests/cli/projects/test-01' in result.output


@skip_if_no_sol_compiler
@pytest.mark.parametrize(
    'path',
    (
        'mortal.sol:Immortal',
        'contracts/mortal.sol:Immortal',
    ),
)
def test_compiling_with_specified_file_and_contract(monkeypatch, path):
    monkeypatch.chdir(os.path.join(this_dir, 'projects/test-01/'))
    runner = CliRunner()
    result = runner.invoke(main, ['compile', path])

    assert result.exit_code == 0, result.output
    assert 'owned.sol' in result.output
    assert 'mortal.sol' in result.output
    assert 'Mortal' not in result.output
    assert 'Immortal' in result.output
    assert ' owned\n' not in result.output
    assert 'tests/cli/projects/test-01' in result.output
