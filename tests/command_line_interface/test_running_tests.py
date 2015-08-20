import re
import click
from click.testing import CliRunner

from populus.cli import main


def test_running_tests_that_pass(monkeypatch):
    monkeypatch.chdir('./tests/command_line_interface/projects/test-03/')
    runner = CliRunner()
    result = runner.invoke(main, ['test'])

    assert result.exit_code == 0, result.output

    # weak assertion but not sure what to do here.
    assert 'test_that_passes' in result.output


def test_running_tests_that_fail(monkeypatch):
    monkeypatch.chdir('./tests/command_line_interface/projects/test-04/')
    runner = CliRunner()
    result = runner.invoke(main, ['test'])

    assert result.exit_code == 0, result.output

    # weak assertion but not sure what to do here.
    assert 'test_that_fails' in result.output
