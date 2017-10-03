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
        "mainnet' and 'morden' are pre-configured to connect to the public "
        "networks.  Other values should be predefined in your populus.ini"
    ),
)
@click.option(
    'wait_for_sync',
    '--wait-for-sync/--no-wait-for-sync',
    default=False,
    help=(
        "Determines whether the deploy command should wait until the chain is "
        "fully synced before deployment"
    ),
)
@click.argument('contracts_to_deploy', nargs=-1)
@click.pass_context
def deploy_cmd(ctx, chain_name, wait_for_sync, contracts_to_deploy):
    """
    Deploys the specified contracts to a chain.
    """
    project = ctx.obj['PROJECT']
    logger = logging.getLogger('populus.cli.deploy')

    deploy(project, logger, chain_name, wait_for_sync, contracts_to_deploy)
