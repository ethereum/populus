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
        max_wait=max_wait,
    )

    #
    # TODO: Dry run to figure out gas costs.
    #
    #dry_run_data_dir = get_geth_data_dir(project_dir, dry_run_chain_name)
    #logfile_path = get_geth_logfile_path(
    #    dry_run_data_dir,
    #    logfile_name_fmt="deploy-dry-run-{0}.log",
    #)

    #ensure_account_exists(dry_run_data_dir)

    #_, dry_run_proc = run_geth_node(dry_run_data_dir, logfile=logfile_path)
    #wait_for_geth_to_start(dry_run_proc)

    #message = (
    #    "======= Executing Dry Run Deploy ========\n"
    #    "Chain Name     : {chain_name}\n"
    #    "Data Directory : {data_dir}\n"
    #    "Geth Logfile   : {logfile_path}\n\n"
    #    "... (deploying)\n"
    #).format(
    #    chain_name=dry_run_chain_name,
    #    data_dir=dry_run_data_dir,
    #    logfile_path=logfile_path,
    #)
    #click.echo(message)

    ## Dry run deploy uses max_gas
    #dry_run_contracts = deploy_contracts(
    #    deploy_client=client,
    #    contracts=contracts,
    #    deploy_at_block=1,
    #    max_wait_for_deploy=60,
    #    from_address=None,
    #    max_wait=60,
    #    contracts_to_deploy=contracts_to_deploy,
    #    dependencies=None,
    #    constructor_args=None,
    #    deploy_gas=None,
    #)
    #validate_deployed_contracts(client, dry_run_contracts)

    #echo_post_deploy_message(client, dry_run_contracts)

    #dry_run_proc.send_signal(signal.SIGINT)
    ## Give the subprocess a SIGINT and give it a few seconds to
    ## cleanup.
    #utils.wait_for_popen(dry_run_proc)

    #def get_deploy_gas(contract_name, contract_class):
    #    max_gas = int(client.get_max_gas() * 0.98)
    #    receipt = dry_run_contracts._deploy_receipts.get(contract_name)
    #    if receipt is None:
    #        return max_gas
    #    gas_used = int(receipt['gasUsed'], 16)
    #    return min(max_gas, int(gas_used * 1.1))

    #deploy_gas = get_deploy_gas

    #
    # Actual deploy
    #
    if not production:
        data_dir = get_geth_data_dir(project_dir, "default")
        logfile_path = get_geth_logfile_path(
            data_dir,
            logfile_name_fmt="deploy-dry-run-{0}.log",
        )

        ensure_account_exists(data_dir)
        _, deploy_proc = run_geth_node(data_dir, logfile=logfile_path)
        wait_for_geth_to_start(deploy_proc)
    elif confirm:
        message = (
            "You are about to deploy contracts to a production environment. "
            "You must have an RPC server that is unlocked running for this to "
            "work.\n\n"
            "Would you like to proceed?"
        )
        if not click.confirm(message):
            raise click.Abort()

    if not dry_run:
        message = (
            "You are about to do a production deploy with no dry run.  Without "
            "a dry run, it isn't feasible to know gas costs and thus deployment "
            "may fail due to long transaction times.\n\n"
            "Are you sure you would like to proceed?"
        )
        if confirm and not click.confirm(message):
            raise click.Abort()

    message = (
        "========== Executing Deploy ===========\n"
        "... (deploying)\n"
        "Chain Name     : {chain_name}\n"
        "Data Directory : {data_dir}\n"
        "Geth Logfile   : {logfile_path}\n\n"
        "... (deploying)\n"
    ).format(
        chain_name="production" if production else "default",
        data_dir="N/A" if production else data_dir,
        logfile_path="N/A" if production else logfile_path,
    )
    click.echo(message)

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
