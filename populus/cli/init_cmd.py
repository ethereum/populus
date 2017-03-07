import os

import click

from populus.config import (
    load_default_config,
    write_config,
)

from populus.utils.config import (
    get_json_config_file_path,
    check_if_json_config_file_exists,
)
from populus.utils.filesystem import (
    ensure_path_exists,
)

from .main import main


TEST_FILE_CONTENTS = """def test_greeter(chain):
    greeter, _ = chain.get_or_deploy_contract('Greeter')

    greeting = greeter.call().greet()
    assert greeting == 'Hello'


def test_custom_greeting(chain):
    greeter, _ = chain.get_or_deploy_contract('Greeter')

    set_txn_hash = greeter.transact().setGreeting('Guten Tag')
    chain.wait.for_receipt(set_txn_hash)

    greeting = greeter.call().greet()
    assert greeting == 'Guten Tag'
"""


GREETER_FILE_CONTENTS = """pragma solidity ^0.4.0;

    contract Greeter {
    string public greeting;

    function Greeter() {
        greeting = 'Hello';
    }

    function setGreeting(string _greeting) public {
        greeting = _greeting;
    }

    function greet() constant returns (string) {
        return greeting;
    }
}
"""


@main.command()
@click.pass_context
def init(ctx):
    """
    Generate project layout with an example contract.
    """
    project = ctx.obj['PROJECT']

    has_json_config = check_if_json_config_file_exists(project.project_dir)

    if has_json_config:
        click.echo(
            "Found existing `populus.json` file.  Not writing default config."
        )
    else:
        json_config_file_path = get_json_config_file_path(project.project_dir)
        default_config = load_default_config()
        write_config(
            project.project_dir,
            default_config,
            json_config_file_path,
        )
        click.echo(
            "Wrote default populus configuration to `./{0}`.".format(
                os.path.relpath(json_config_file_path, project.project_dir),
            )
        )

    project.load_config()

    if ensure_path_exists(project.contracts_dir):
        click.echo(
            "Created Directory: ./{0}".format(
                os.path.relpath(project.contracts_dir)
            )
        )

    example_contract_path = os.path.join(project.contracts_dir, 'Greeter.sol')
    if not os.path.exists(example_contract_path):
        with open(example_contract_path, 'w') as example_contract_file:
            example_contract_file.write(GREETER_FILE_CONTENTS)
        click.echo("Created Example Contract: ./{0}".format(
            os.path.relpath(example_contract_path)
        ))

    tests_dir = os.path.join(project.project_dir, 'tests')
    if ensure_path_exists(tests_dir):
        click.echo("Created Directory: ./{0}".format(os.path.relpath(tests_dir)))

    example_tests_path = os.path.join(tests_dir, 'test_greeter.py')
    if not os.path.exists(example_tests_path):
        with open(example_tests_path, 'w') as example_tests_file:
            example_tests_file.write(TEST_FILE_CONTENTS)
        click.echo("Created Example Tests: ./{0}".format(
            os.path.relpath(example_tests_path)
        ))
