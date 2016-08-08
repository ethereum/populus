import os

import click

from geth import (
    DevGethProcess,
)

from web3 import (
    Web3,
    IPCProvider,
)

from populus.utils.contracts import (
    load_compiled_contract_json,
)
from populus.utils.transactions import (
    wait_for_block_number,
)
from populus.compilation import (
    compile_and_write_contracts,
)
from populus.deployment import (
    deploy_contracts,
    validate_deployed_contracts,
)

from .main import main


def echo_post_deploy_message(web3, deployed_contracts):
    message = (
        "========== Deploy Completed ==========\n"
        "Deployed {n} contracts:"
    ).format(
        n=len(deployed_contracts),
    )
    click.echo(message)
    for contract_name, deployed_contract in deployed_contracts:
        deploy_receipt = web3.eth.getTransactionReceipt(deployed_contract.deploy_txn_hash)
        gas_used = deploy_receipt['gasUsed']
        deploy_txn = web3.eth.getTransaction(deploy_receipt['transactionHash'])
        gas_provided = deploy_txn['gas']
        click.echo("- {0} ({1}) gas: {2} / {3}".format(
            contract_name,
            deployed_contract.address,
            gas_used,
            gas_provided,
        ))


@main.command('deploy')
@click.option(
    '--confirm/--no-confirm',
    default=True,
    help="Bypass any confirmation prompts",
)
# Deploy chain config
@click.option(
    '--chain',
    '-c',
    default='default',
    help="Specify which chain to deploy to.",
)
# Compilation config
@click.option(
    '--compile/--no-compile',
    default=True,
    help="Should contracts be compiled",
)
@click.option(
    '--optimize/--no-optimize',
    default=True,
    help="Should contracts be compiled with the --optimize flag.",
)
@click.argument('contracts_to_deploy', nargs=-1)
def deploy(chain, confirm, compile, optimize, contracts_to_deploy):
    """
    Deploys the specified contracts via the RPC client.
    """
    # TODO: project_dir should happen up at the `main` level
    project_dir = os.getcwd()

    if compile:
        compile_and_write_contracts(project_dir, optimize=optimize)

    compiled_contract = load_compiled_contract_json(project_dir)

    # TODO: what if the user wants to run geth themselves.
    with DevGethProcess(chain_name=chain, base_dir=project_dir) as geth:
        geth.wait_for_dag(600)
        geth.wait_for_ipc(30)

        web3 = Web3(IPCProvider(geth.ipc_path))

        wait_for_block_number(web3, 1, 120)

        if confirm:
            message = (
                "You are about to deploy contracts to a production environment. "
                "You must have an RPC server that is unlocked running for this to "
                "work.\n\n"
                "Would you like to proceed?"
            )
            if not click.confirm(message):
                raise click.Abort()

        deployed_contracts = deploy_contracts(
            web3,
            compiled_contract,
            contracts_to_deploy or None,
            timeout=120,
        )
        validate_deployed_contracts(web3, deployed_contracts)
        echo_post_deploy_message(web3, deployed_contracts)
