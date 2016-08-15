import os

import click

from populus.utils.filesystem import (
    ensure_path_exists
)

from .main import main


@main.command()
@click.pass_context
def init(ctx):
    """
    Generate project layout with an example contract.
    """
    project = ctx.obj['PROJECT']

    if not os.path.exists(project.primary_config_file_path):
        with open(project.primary_config_file_path, 'w') as config_file:
            config_file.write("[populus]\n")
            config_file.write("project_dir = {0}".format(
                os.path.relpath(project.project_dir)
            ))

    if ensure_path_exists(project.contracts_dir):
        click.echo(
            "Created Directory: ./{0}".format(
                os.path.relpath(project.contracts_dir)
            )
        )

    example_contract_path = os.path.join(project.contracts_dir, 'Example.sol')
    if not os.path.exists(example_contract_path):
        with open(example_contract_path, 'w') as example_contract_file:
            example_contract_file.write(
                'contract Example {\n    function Example() {\n    }\n}\n'
            )
        click.echo("Created Example Contract: ./{0}".format(
            os.path.relpath(example_contract_path)
        ))

    tests_dir = os.path.join(project.project_dir, 'tests')
    if ensure_path_exists(tests_dir):
        click.echo("Created Directory: ./{0}".format(os.path.relpath(tests_dir)))

    example_tests_path = os.path.join(tests_dir, 'test_example.py')
    if not os.path.exists(example_tests_path):
        with open(example_tests_path, 'w') as example_tests_file:
            example_tests_file.write('def test_it(deployed_contracts):\n    example = deployed_contracts.Example\n    assert example.address\n')  # NOQA
        click.echo("Created Example Tests: ./{0}".format(
            os.path.relpath(example_tests_path)
        ))
