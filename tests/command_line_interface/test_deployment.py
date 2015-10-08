import re
import click
from click.testing import CliRunner

from populus.cli import main


def test_deployment(testrpc_server, monkeypatch):
    monkeypatch.chdir('./tests/command_line_interface/projects/test-02/')
    runner = CliRunner()
    result = runner.invoke(main, ['deploy'])

    assert result.exit_code == 0, result.output

    # weak assertion but not sure what to do here.
    assert 'owned' in result.output
    assert re.search(' (0x[0-9a-f]{40}) ', result.output)
    assert re.search(' (txn:0x[0-9a-f]{64})', result.output)
