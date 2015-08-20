import os

import click

from populus import utils
from eth_rpc_client import Client


@click.group()
def main():
    pass


@main.command()
def compile():
    """
    Compile contracts.
    """
    click.echo('Compiling!')
    contract_source_paths = utils.get_contract_files(os.getcwd())

    compiled_sources = {}

    for source_path in contract_source_paths:
        try:
            compiler = utils.get_compiler_for_file(source_path)
        except ValueError:
            raise click.ClickException("No compiler available for {0}".format(source_path))
        with open(source_path) as source_file:
            source_code = source_file.read()

        compiled_sources.update(utils._compile_rich(compiler, source_code))

    utils.write_compiled_sources(os.getcwd(), compiled_sources)


@main.command()
def deploy():
    """
    Deploy contracts.
    """
    contracts = utils.load_contracts(os.getcwd())
    client = Client('127.0.0.1', '8545')

    deployed_contracts = utils.deploy_contracts(client, contracts)

    name_padding = max(len(n) + 1 for n in deployed_contracts.keys())
    for name, info in deployed_contracts.items():
        click.echo("{name} @ {addr} via txn:{txn_hash}".format(
            name=name.ljust(name_padding),
            addr=(info.get('addr') or '<pending>').ljust(42),
            txn_hash=info['txn'].ljust(66),
        ))


@main.command()
def test():
    """
    Test contracts (wrapper around py-test)
    """
    import pytest
    pytest.main(os.path.join(os.getcwd(), 'tests'))
