import os
import re
import click
import pytest
from click.testing import CliRunner

from populus.cli import main


this_dir = os.path.dirname(__file__)


def test_deployment(monkeypatch):
    monkeypatch.chdir(os.path.join(this_dir, 'projects/test-02/'))
    runner = CliRunner()
    result = runner.invoke(main, ['deploy', '--no-confirm', 'owned'])

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'owned' in result.output
    assert re.search('owned \(0x[0-9a-f]{40}\)', result.output)
