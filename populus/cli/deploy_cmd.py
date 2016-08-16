import gevent

import click

from populus.utils.transactions import (
    is_account_locked,
    wait_for_unlock,
)
from populus.utils.cli import (
    select_chain,
    select_account,
    request_account_unlock,
    show_chain_sync_progress,
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
    'deploy_from',
    '--deploy-from',
    '-d',
    help=(
        "Specifies the account that should be used for deploys.  You can "
        "specify either the full account address, or the integer 0 based index "
        "of the account in the account list."
    ),
)
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
@click.argument('contracts_to_deploy', nargs=-1)
@click.pass_context
def deploy(ctx, chain_name, deploy_from, contracts_to_deploy):
    """
    Deploys the specified contracts via the RPC client.
    """
    project = ctx.obj['PROJECT']

    # Determine which chain should be used.
    if not chain_name:
        chain_name = select_chain(project)

    chain_section_name = "chain:{0}".format(chain_name)

    chain_config = project.config.chains[chain_name]

    compiled_contracts = project.compiled_contracts

    chain = project.get_chain(chain_name)

    with chain:
        web3 = chain.web3

        if chain_name in {'mainnet', 'morden'}:
            show_chain_sync_progress(chain)

        # Choose the address we should deploy from.
        # TODO: this set of if blocks should be it's own helper function.
        if deploy_from:
            if deploy_from in web3.eth.accounts:
                account = deploy_from
            elif deploy_from.isdigit() and int(deploy_from) < len(web3.eth.accounts):
                account = web3.eth.accounts[int(deploy_from)]
            else:
                raise click.Abort(
                    "The account {0!r} was not found in the list of accounts "
                    "for chain {1!r}.".format(
                        account,
                        chain_name,
                    )
                )
        elif 'deploy_from' in chain_config:
            account = chain_config['deploy_from']
            if account not in web3.eth.accounts:
                raise click.Abort(
                    "The chain {0!r} is configured to deploy from account {1!r} "
                    "which was not found in the account list for this chain. "
                    "Please ensure that this account exists.".format(
                        chain_name,
                        account,
                    )
                )
        else:
            account = select_account(chain)
            set_as_deploy_from_msg = (
                "Would you like set the address '{0}' as the default"
                "`deploy_from` address for the '{1}' chain?".format(
                    account,
                    chain_name,
                )
            )
            if click.confirm(set_as_deploy_from_msg):
                project.config.set(chain_section_name, 'deploy_from', account)
                click.echo(
                    "Wrote updated chain configuration to '{0}'".format(
                        project.write_config()
                    )
                )

        # Unlock the account if needed.
        if is_account_locked(web3, account):
            try:
                wait_for_unlock(web3, account, 2)
            except gevent.Timeout:
                request_account_unlock(chain, account, None)

        # Configure web3 to now send from our chosen account by default
        web3.eth.defaultAccount = account

        deployed_contracts = deploy_contracts(
            web3,
            compiled_contracts,
            contracts_to_deploy or None,
            timeout=120,
        )
        validate_deployed_contracts(web3, deployed_contracts)
        echo_post_deploy_message(web3, deployed_contracts)
