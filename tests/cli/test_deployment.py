import os
import re
import click
import pytest
from click.testing import CliRunner

from populus.cli import main


this_dir = os.path.dirname(__file__)


def test_deployment_command_with_no_specified_contracts(project_dir,
                                                        write_project_file,
                                                        MATH,
                                                        SIMPLE_CONSTRUCTOR,):
    write_project_file('./contracts/Math.sol', MATH['source'])
    write_project_file('./contracts/SimpleConstructor.sol', SIMPLE_CONSTRUCTOR['source'])
    runner = CliRunner()
    result = runner.invoke(main, ['deploy', '--no-confirm'])

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Math' in result.output
    assert re.search('Math \(0x[0-9a-f]{40}\)', result.output)

    assert 'WithNoArgumentConstructor' in result.output
    assert re.search('WithNoArgumentConstructor \(0x[0-9a-f]{40}\)', result.output)
