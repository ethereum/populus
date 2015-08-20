import pytest
import click
from click.testing import CliRunner

from ethereum._solidity import get_solidity

from populus.cli import main


@pytest.mark.skipif(get_solidity() is None, reason="'solc' compiler not available")
def test_compiling(monkeypatch):
    monkeypatch.chdir('./tests/command_line_interface/projects/test-01/')
    runner = CliRunner()
    result = runner.invoke(main, ['compile'])

    assert result.exit_code == 0, result.output
    assert result.output == 'Compiling!\n'
