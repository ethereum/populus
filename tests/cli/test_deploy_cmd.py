import os
import re
import click
import pytest
from click.testing import CliRunner
from flaky import flaky

from populus.cli import main


@flaky
def test_deployment_command_with_no_specified_contracts(project_dir,
                                                        write_project_file,
                                                        MATH,
                                                        SIMPLE_CONSTRUCTOR):
    write_project_file('./contracts/Math.sol', MATH['source'])
    write_project_file('./contracts/SimpleConstructor.sol', SIMPLE_CONSTRUCTOR['source'])
    runner = CliRunner()
    result = runner.invoke(main, ['deploy'], input=(
        'testrpc\n'  # select the local chain.
        '0\n'      # select account to deploy from.
        'Y\n'      # write it to config file
    ))

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Math' in result.output
    assert re.search('Math \(0x[0-9a-f]{40}\)', result.output)

    assert 'WithNoArgumentConstructor' in result.output
    assert re.search('WithNoArgumentConstructor \(0x[0-9a-f]{40}\)', result.output)


@flaky
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
        'deploy', 'Math', 'Emitter', '--chain', 'testrpc', '--deploy-from', '0'
    ])

    assert result.exit_code == 0, result.output + str(result.exception)

    # weak assertion but not sure what to do here.
    assert 'Math' in result.output
    assert re.search('Math \(0x[0-9a-f]{40}\)', result.output)

    assert 'WithNoArgumentConstructor' not in result.output
    assert not re.search('WithNoArgumentConstructor \(0x[0-9a-f]{40}\)', result.output)

    assert 'Emitter' in result.output
    assert re.search('Emitter \(0x[0-9a-f]{40}\)', result.output)
