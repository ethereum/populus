import os

import click
import signal

from eth_rpc_client import Client

from populus import utils
from populus.contracts import package_contracts
from populus.geth import (
    get_geth_data_dir,
    get_geth_logfile_path,
    ensure_account_exists,
    run_geth_node,
    wait_for_geth_to_start,
    add_to_known_contracts,
)
from populus.deployment import (
    deploy_contracts,
    validate_deployed_contracts,
)

from .main import main


def echo_post_deploy_message(deploy_client, deployed_contracts):
    message = (
        "========== Deploy Completed ==========\n"
        "Deployed {n} contracts:"
    ).format(
        n=len(deployed_contracts),
    )
    click.echo(message)
    for contract_name, deployed_contract in deployed_contracts:
        receipt = deployed_contracts._deploy_receipts[contract_name]
        gas_used = int(
            receipt['gasUsed'],
            16,
        )
        txn = deploy_client.get_transaction_by_hash(receipt['transactionHash'])
        gas_provided = int(txn['gas'], 16)
        click.echo("- {0} ({1}) gas: {2} / {3}".format(
            contract_name,
            deployed_contract._meta.address,
            gas_used,
            gas_provided,
        ))


@main.command()
@click.option(
    '--dry-run',
    '-d',
    is_flag=True,
    default=None,
    help=(
        "Do a dry run deploy first.  When doing a production deploy, you should "
        "always do a dry run so that deploy gas prices can be known."
    ),
)
@click.option(
    '--dry-run-chain-name',
    '-n',
    type=click.STRING,
    default="default",
    help=(
        "Specifies the chain name that should be used for the dry run "
        "deployment.  Defaults to 'default'"
    ),
)
@click.option(
    '--production',
    '-p',
    is_flag=True,
    help="Deploy to a production chain (RPC server must be run manually)",
)
@click.option(
    '--confirm/--no-confirm',
    default=True,
    help="Bypass any confirmation prompts",
)
@click.option(
    '--record/--no-record',
    default=True,
    help=(
        "Record the created contracts in the 'known_contracts' lists. "
        "This only works for non-production chains."
    ),
)
@click.argument('contracts_to_deploy', nargs=-1)
def deploy(dry_run, dry_run_chain_name, production, confirm, record, contracts_to_deploy):
    """
    Deploys the specified contracts via the RPC client.
    """
    if dry_run is None:
        # If we are doing a production deploy and dry_run was not specified,
        # then default to True
        dry_run = production

    client = Client("127.0.0.1", "8545")
    project_dir = os.getcwd()
    deploy_gas = None

    contracts = package_contracts(utils.load_contracts(project_dir))

    if dry_run:
        dry_run_data_dir = get_geth_data_dir(project_dir, dry_run_chain_name)
        logfile_path = get_geth_logfile_path(
            dry_run_data_dir,
            logfile_name_fmt="deploy-dry-run-{0}.log",
        )

        ensure_account_exists(dry_run_data_dir)

        _, dry_run_proc = run_geth_node(dry_run_data_dir, logfile=logfile_path)
        wait_for_geth_to_start(dry_run_proc)

        message = (
            "======= Executing Dry Run Deploy ========\n"
            "Chain Name     : {chain_name}\n"
            "Data Directory : {data_dir}\n"
            "Geth Logfile   : {logfile_path}\n\n"
            "... (deploying)\n"
        ).format(
            chain_name=dry_run_chain_name,
            data_dir=dry_run_data_dir,
            logfile_path=logfile_path,
        )
        click.echo(message)

        # Dry run deploy uses max_gas
        dry_run_contracts = deploy_contracts(
            deploy_client=client,
            contracts=contracts,
            deploy_at_block=1,
            max_wait_for_deploy=60,
            from_address=None,
            max_wait=60,
            contracts_to_deploy=contracts_to_deploy,
            dependencies=None,
            constructor_args=None,
            deploy_gas=None,
        )
        validate_deployed_contracts(client, dry_run_contracts)

        echo_post_deploy_message(client, dry_run_contracts)

        dry_run_proc.send_signal(signal.SIGINT)
        # Give the subprocess a SIGINT and give it a few seconds to
        # cleanup.
        utils.wait_for_popen(dry_run_proc)

        def get_deploy_gas(contract_name, contract_class):
            max_gas = int(client.get_max_gas() * 0.98)
            receipt = dry_run_contracts._deploy_receipts.get(contract_name)
            if receipt is None:
                return max_gas
            gas_used = int(receipt['gasUsed'], 16)
            return min(max_gas, int(gas_used * 1.1))

        deploy_gas = get_deploy_gas

    contracts = package_contracts(utils.load_contracts(project_dir))

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
