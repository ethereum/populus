import os
import re
import click
import pytest
from click.testing import CliRunner

from populus.cli import main


def test_deployment_command_with_one_specified_contract(project_dir,
                                                        write_project_file,
                                                        MATH,
                                                        SIMPLE_CONSTRUCTOR):
    write_project_file('./contracts/Math.sol', MATH['source'])
    write_project_file('./contracts/SimpleConstructor.sol', SIMPLE_CONSTRUCTOR['source'])
    runner = CliRunner()
    result = runner.invoke(main, ['deploy', 'Math'], input=(
        'temp\n'  # select the local chain.
        '0\n'      # select account to deploy from.
        'Y\n'      # write it to config file
    ))

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Math' in result.output
    assert 'WithNoArgumentConstructor' not in result.output


def test_deployment_command_with_specified_contracts(project_dir,
                                                     write_project_file,
                                                     MATH,
                                                     SIMPLE_CONSTRUCTOR,
                                                     EMITTER):
    write_project_file('./contracts/Math.sol', MATH['source'])
    write_project_file('./contracts/SimpleConstructor.sol', SIMPLE_CONSTRUCTOR['source'])
    write_project_file('./contracts/Emitter.sol', EMITTER['source'])
    runner = CliRunner()
    result = runner.invoke(main, [
        'deploy', 'Math', 'Emitter', '--chain', 'temp',
    ])

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Math' in result.output
    assert 'WithNoArgumentConstructor' not in result.output
    assert 'Emitter' in result.output


def test_deployment_command_with_prompt_for_contracts(project_dir,
                                                      write_project_file,
                                                      MATH,
                                                      SIMPLE_CONSTRUCTOR,
                                                      EMITTER):
    write_project_file('./contracts/Math.sol', MATH['source'])
    write_project_file('./contracts/SimpleConstructor.sol', SIMPLE_CONSTRUCTOR['source'])
    write_project_file('./contracts/Emitter.sol', EMITTER['source'])
    runner = CliRunner()
    result = runner.invoke(main, [
        'deploy', '--chain', 'temp',
    ], input='Math\n')

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Math' in result.output
    assert 'WithNoArgumentConstructor' in result.output
    assert 'Emitter' in result.output
    assert 'Deploying Math' in result.output
