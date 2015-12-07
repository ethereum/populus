import re
import click
import pytest
from click.testing import CliRunner

from populus.cli import main
from populus.geth import (
    is_geth_available,
)


skip_if_no_geth = pytest.mark.skipif(
    not is_geth_available(),
    reason="'geth' not available",
)


@skip_if_no_geth
def test_deployment(monkeypatch):
    monkeypatch.chdir('./tests/cli/projects/test-02/')
    runner = CliRunner()
    result = runner.invoke(main, ['deploy', '--no-confirm', 'owned'])

    assert result.exit_code == 0, result.output

    # weak assertion but not sure what to do here.
    assert 'owned' in result.output
    assert re.search('owned \(0x[0-9a-f]{40}\)', result.output)
