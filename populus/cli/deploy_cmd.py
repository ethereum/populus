from __future__ import absolute_import
import logging

import click

from populus.api.deploy import (
    deploy,
)

from .main import main


@main.command('deploy')
@click.option(
    'chain_name',
    '--chain',
    '-c',
    help=(
        "Specifies the chain that contracts should be deployed to. The chains "
        "'mainnet' and 'ropsten' are pre-configured to connect to the public "
        "networks, 'tester' and 'testrpc' are pre-configured tests chains, "
        "'web3tester' provides the web3.py Web3EthereumTesterProvider. "
        "Other values should be predefined in your populus config files"
    ),
    default=None,
)
@click.option(
    'rpc_path',
    '--rpc-path',
    '-r',
    help=(
        "Specify http or https to the rpc node, "
        "e.g. https://mainnet.infura.io"
    ),
    default=None,
)
@click.option(
    'ipc_path',
    '--ipc-path',
    '-i',
    help=(
        "Specify a path to the ipc socket of the geth instance, "
        "e.g. /home/username/.ethereum/geth/geth.ipc"
    ),
    default=None,
)
@click.option(
    'wait_for_sync',
    '--wait-for-sync/--no-wait-for-sync',
    default=True,
    help=(
        "Determines whether the deploy command should wait until the chain is "
        "fully synced before deployment"
    ),
)
@click.argument('contracts_to_deploy', nargs=-1)
@click.pass_context
def deploy_cmd(ctx, chain_name, wait_for_sync, contracts_to_deploy, rpc_path, ipc_path):
    """
    Deploys the specified contracts to a chain.
    """

    project = ctx.obj['PROJECT']
    logger = logging.getLogger('populus.cli.deploy')

    deploy(
        project,
        logger,
        wait_for_sync,
        contracts_to_deploy,
        chain_name,
        rpc_path,
        ipc_path
    )
