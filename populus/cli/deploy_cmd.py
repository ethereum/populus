from __future__ import absolute_import

import logging

import click

from populus.api.deploy import (
    deploy,
)

from .main import main


def echo_post_deploy_message(web3, deployed_contracts):
    logger = logging.getLogger('populus.cli.deploy.echo_post_deploy_message')

    message = (
        "========== Deploy Completed ==========\n"
        "Deployed {n} contracts:"
    ).format(
        n=len(deployed_contracts),
    )
    logger.info(message)
    for contract_name, deployed_contract in deployed_contracts:
        deploy_receipt = web3.eth.getTransactionReceipt(deployed_contract.deploy_txn_hash)
        gas_used = deploy_receipt['gasUsed']
        deploy_txn = web3.eth.getTransaction(deploy_receipt['transactionHash'])
        gas_provided = deploy_txn['gas']
        logger.info("- {0} ({1}) gas: {2} / {3}".format(
            contract_name,
            deployed_contract.address,
            gas_used,
            gas_provided,
        ))


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
    default="tester",
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
@click.pass_context
def deploy_cmd(ctx, chain_name, wait_for_sync):
    """
    Deploys the specified contracts to a chain.
    """
    logger = logging.getLogger('populus.cli.deploy')
    project_root_dir = ctx.obj['project_root_dir']
    user_config_path = ctx.obj['user_config_path']
    deploy(project_root_dir, chain_name, user_config_path, wait_for_sync, logger)
