import pytest

import os
import re

import click

from click.testing import CliRunner

from populus.cli import main
from populus.utils.testing import load_contract_fixture


@load_contract_fixture('Math.sol')
@load_contract_fixture('WithNoArgumentConstructor.sol')
@load_contract_fixture('Emitter.sol')
def test_deployment_command_project_default_chain(project):
    runner = CliRunner()
    result = runner.invoke(main, ['deploy', '--no-wait-for-sync'])

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Deploying Math' in result.output
    assert 'Deploying WithNoArgumentConstructor' in result.output
    assert 'Deploying Emitter' in result.output
