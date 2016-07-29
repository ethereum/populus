import os

import click

from populus.utils.filesystem import (
    get_contracts_dir, ensure_path_exists
)

from .main import main


@main.command()
def init():
    """
    Generate project layout with an example contract.
    """
    project_dir = os.getcwd()

    contracts_dir = get_contracts_dir(project_dir)
    if ensure_path_exists(contracts_dir):
        click.echo("Created Directory: ./{0}".format(os.path.relpath(contracts_dir)))

    example_contract_path = os.path.join(contracts_dir, 'Example.sol')
    if not os.path.exists(example_contract_path):
        with open(example_contract_path, 'w') as example_contract_file:
            example_contract_file.write('contract Example {\n        function Example() {\n        }\n}\n')  # NOQA
        click.echo("Created Example Contract: ./{0}".format(os.path.relpath(example_contract_path)))  # NOQA

    tests_dir = os.path.join(project_dir, 'tests')
    if ensure_path_exists(tests_dir):
        click.echo("Created Directory: ./{0}".format(os.path.relpath(tests_dir)))

    example_tests_path = os.path.join(tests_dir, 'test_example.py')
    if not os.path.exists(example_tests_path):
        with open(example_tests_path, 'w') as example_tests_file:
            example_tests_file.write('def test_it(deployed_contracts):\n    example = deployed_contracts.Example\n    assert example.address\n')  # NOQA
        click.echo("Created Example Tests: ./{0}".format(os.path.relpath(example_tests_path)))  # NOQA
