import os
import re

import click
from click.testing import CliRunner

from populus.cli import main
from populus.utils.testing import load_contract_fixture


@load_contract_fixture('Math.sol')
@load_contract_fixture('WithNoArgumentConstructor.sol')
def test_deployment_command_with_one_specified_contract(project):
    runner = CliRunner()
    result = runner.invoke(main, ['deploy', '--no-wait-for-sync', 'Math'], input=(
        'tester\n'  # select the local chain.
        '0\n'       # select account to deploy from.
        'Y\n'       # write it to config file
    ))

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Deploying Math' in result.output
    assert 'Deploying WithNoArgumentConstructor' not in result.output


@load_contract_fixture('Math.sol')
@load_contract_fixture('WithNoArgumentConstructor.sol')
@load_contract_fixture('Emitter.sol')
def test_deployment_command_with_specified_contracts(project):
    runner = CliRunner()
    result = runner.invoke(main, [
        'deploy', '--no-wait-for-sync', 'Math', 'Emitter', '--chain', 'tester',
    ])

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Deploying Math' in result.output
    assert 'Deploying WithNoArgumentConstructor' not in result.output
    assert 'Deploying Emitter' in result.output


@load_contract_fixture('Math.sol')
@load_contract_fixture('WithNoArgumentConstructor.sol')
@load_contract_fixture('Emitter.sol')
def test_deployment_command_with_prompt_for_contracts(project):
    runner = CliRunner()
    result = runner.invoke(main, [
        'deploy', '--chain', 'tester', '--no-wait-for-sync',
    ], input='Math\n')

    assert result.exit_code == 0, result.output + str(result.exception)

    assert 'Deploying Math' in result.output
    assert 'Deploying Emitter' not in result.output
    assert 'Deploying WithNoArgumentConstructor' not in result.output
