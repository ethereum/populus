import os

import click

from eth_rpc_client import Client

from populus import utils

from .main import main


@main.command()
def deploy():
    """
    Deploy contracts.

    TODO: this command is dangerous.  Probably needs some reworking.
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
