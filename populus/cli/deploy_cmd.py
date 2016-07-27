import os

import click
import signal

from web3 import (
    Web3,
    IPCProvider,
)
from web3.providers.rpc import (
    TestRPCProvider,
)

from populus.utils.networking import (
    get_open_port,
)
from populus.utils.contracts import (
    package_contracts,
    load_compiled_contract_json,
)
from populus.compilation import (
    compile_and_write_contracts,
)
from populus.deployment import (
    deploy_contracts,
    validate_deployed_contracts,
)
from populus.chain import (
    dev_geth_process,
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
        deploy_receipt = deployed_contracts._deploy_receipts[contract_name]
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
    is_flag=True,
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

    # TODO: web3 setup should happen up at the `main` level
    dry_run_web3 = Web3(TestRPCProvider(port=get_open_port()))

    dry_run_contracts = package_contracts(dry_run_web3, compiled_contract)

    dry_run_deployed_contracts = deploy_contracts(
        web3=dry_run_web3,
        all_contracts=dry_run_contracts,
        timeout=60,
    )
    validate_deployed_contracts(dry_run_web3, dry_run_deployed_contracts)

    # TODO: what if the user wants to run geth themselves.
    with dev_geth_process(project_dir, chain) as geth:
        geth.wait_for_dag(600)
        geth.wait_for_ipc(30)

        web3 = Web3(IPCProvider(geth.ipc_path))

        def get_deploy_gas(contract_class):
            gas_limit = get_block_gas_limit(web3)
            max_gas = 98 * gas_limit // 100
            receipt = web3.eth.getTransactionReceipt(contract_class.deploy_txn_hash)

            if receipt is None:
                return max_gas

            gas_used = receipt['gasUsed']
            return min(max_gas, 110 * gas_used // 100))


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
        deploy_client=client,
        contracts=contracts,
        deploy_at_block=1,
        max_wait_for_deploy=120,
        from_address=None,
        max_wait=120,
        contracts_to_deploy=contracts_to_deploy,
        dependencies=None,
        constructor_args=None,
        deploy_gas=deploy_gas,
    )
    validate_deployed_contracts(client, deployed_contracts)

    echo_post_deploy_message(client, deployed_contracts)

    if not production:
        if record:
            add_to_known_contracts(deployed_contracts, data_dir)

        deploy_proc.send_signal(signal.SIGINT)
        # Give the subprocess a SIGINT and give it a few seconds to
        # cleanup.
        utils.wait_for_popen(deploy_proc)
