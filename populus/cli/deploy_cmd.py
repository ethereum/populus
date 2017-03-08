import click

from populus.utils.cli import (
    select_chain,
    show_chain_sync_progress,
    deploy_contract_and_verify,
    select_project_contract,
)
from populus.utils.deploy import (
    get_deploy_order,
)

from .main import main


def echo_post_deploy_message(web3, deployed_contracts):
    # TODO: update this message.
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
def deploy_cmd(ctx, chain_name, contracts_to_deploy):
    """
    Deploys the specified contracts to a chain.
    """
    project = ctx.obj['PROJECT']

    # Determine which chain should be used.
    if not chain_name:
        chain_name = select_chain(project)

    compiled_contracts = project.compiled_contracts

    if contracts_to_deploy:
        # validate that we *know* about all of the contracts
        unknown_contracts = set(contracts_to_deploy).difference(
            compiled_contracts.keys()
        )
        if unknown_contracts:
            unknown_contracts_message = (
                "Some contracts specified for deploy were not found in the "
                "compiled project contracts.  These contracts could not be found "
                "'{0}'.  Searched these known contracts '{1}'".format(
                    ', '.join(sorted(unknown_contracts)),
                    ', '.join(sorted(compiled_contracts.keys())),
                )
            )
            raise click.ClickException(unknown_contracts_message)
    else:
        # prompt the user to select the desired contracts they want to deploy.
        # Potentially display the currently deployed status.
        contracts_to_deploy = [select_project_contract(project)]

    with project.get_chain(chain_name) as chain:
        provider = chain.provider
        registrar = chain.registrar

        if chain_name in {'mainnet', 'morden'}:
            show_chain_sync_progress(chain)

        # Get the deploy order.
        deploy_order = get_deploy_order(
            contracts_to_deploy,
            compiled_contracts,
        )

        # Display Start Message Info.
        starting_msg = (
            "Beginning contract deployment.  Deploying {0} total contracts ({1} "
            "Specified, {2} because of library dependencies)."
            "\n\n" +
            (" > ".join(deploy_order.keys()))
        ).format(
            len(deploy_order),
            len(contracts_to_deploy),
            len(deploy_order) - len(contracts_to_deploy),
        )
        click.echo(starting_msg)

        for contract_name, _ in deploy_order.items():
            if not provider.are_contract_dependencies_available(contract_name):
                raise ValueError(
                    "Something is wrong with the deploy order.  Some "
                    "dependencies for {0} are not "
                    "available.".format(contract_name)
                )

            # Check if we already have an existing deployed version of that
            # contract (via the registry).  For each of these, prompt the user
            # if they would like to use the existing version.
            if provider.is_contract_available(contract_name):
                # TODO: this block should be a standalone cli util.
                # TODO: this block needs to use the `Provider` API
                existing_contract_instance = provider.get_contract(contract_name)
                found_existing_contract_prompt = (
                    "Found existing version of {name} in registrar. "
                    "Would you like to use the previously deployed "
                    "contract @ {address}?".format(
                        name=contract_name,
                        address=existing_contract_instance.address,
                    )
                )
                if click.prompt(found_existing_contract_prompt, default=True):
                    continue

            # We don't have an existing version of this contract available so
            # deploy it.
            contract_instance = deploy_contract_and_verify(
                chain,
                contract_name=contract_name,
            )

            # Store the contract address for linking of subsequent deployed contracts.
            registrar.set_contract_address(contract_name, contract_instance.address)

        # TODO: fix this message.
        success_msg = (
            "Deployment Successful."
        )
        click.echo(success_msg)
