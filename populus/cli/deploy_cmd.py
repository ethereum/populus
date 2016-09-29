import click

from collections import OrderedDict

from populus.utils.cli import (
    select_chain,
    show_chain_sync_progress,
    get_unlocked_deploy_from_address,
    deploy_contract_and_verify,
    select_project_contract,
)
from populus.utils.deploy import (
    get_deploy_order,
)
from populus.migrations.registrar import (
    get_contract_from_registrar,
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

    chain = project.get_chain(chain_name)
    deployed_contracts = OrderedDict()

    with chain:
        web3 = chain.web3

        if chain_name in {'mainnet', 'morden'}:
            show_chain_sync_progress(chain)

        if deploy_from is None:
            deploy_from = get_unlocked_deploy_from_address(chain)
        elif deploy_from not in web3.eth.accounts:
            try:
                deploy_from = web3.eth.accounts[int(deploy_from)]
            except IndexError:
                raise click.ClickException(
                    "Unknown deploy_from account: {0}".format(deploy_from)
                )

        web3.eth.defaultAccount = deploy_from

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
            link_dependencies = {
                contract_name: contract.address
                for contract_name, contract
                in deployed_contracts.items()
            }
            contract_factory = chain.contract_factories[contract_name]

            # Check if we already have an existing deployed version of that
            # contract (via the registry).  For each of these, prompt the user
            # if they would like to use the existing version.
            if contract_name not in contracts_to_deploy and chain.has_registrar:
                # TODO: this block should be a standalone cli util.
                existing_contract = get_contract_from_registrar(
                    chain=chain,
                    contract_name=contract_name,
                    contract_factory=contract_factory,
                    link_dependencies=link_dependencies,
                )
                if existing_contract:
                    found_existing_contract_prompt = (
                        "Found existing version of {name} in registrar. "
                        "Would you like to use the previously deployed "
                        "contract @ {address}?".format(
                            name=contract_name,
                            address=existing_contract.address,
                        )
                    )
                    if click.prompt(found_existing_contract_prompt):
                        deployed_contracts[contract_name] = existing_contract
                        continue

            # We don't have an existing version of this contract available so
            # deploy it.
            contract = deploy_contract_and_verify(
                chain,
                contract_name=contract_name,
                link_dependencies=link_dependencies,
            )

            if chain.has_registrar:
                # TODO: this block should be a standalone cli util.
                contract_key = 'contract/{name}'.format(name=contract_name)
                register_txn_hash = chain.registrar.transact().setAddress(
                    contract_key, contract.address
                )
                register_msg = (
                    "Registering contract '{name}' @ {address} "
                    "in registrar in txn: {txn_hash} ...".format(
                        name=contract_name,
                        address=contract.address,
                        txn_hash=register_txn_hash,
                    )
                )
                click.echo(register_msg, nl=False)
                chain.wait.for_receipt(register_txn_hash, timeout=180)
                click.echo(' DONE')
            deployed_contracts[contract_name] = contract

        # TODO: fix this message.
        success_msg = (
            "Deployment Successful."
        )
        click.echo(success_msg)
