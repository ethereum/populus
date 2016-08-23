import click

from populus.utils.cli import (
    select_chain,
    show_chain_sync_progress,
    get_unlocked_deploy_from_address,
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

    compiled_contracts = project.compiled_contracts

    chain = project.get_chain(chain_name)

    with chain:
        web3 = chain.web3

        if chain_name in {'mainnet', 'morden'}:
            show_chain_sync_progress(chain)

        account = get_unlocked_deploy_from_address(chain)
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
