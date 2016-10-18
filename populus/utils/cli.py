import os
import itertools
import random

import click

import gevent

from populus.observers import (
    DirWatcher,
)
from populus.compilation import (
    compile_and_write_contracts,
)
from .deploy import (
    deploy_contract,
)
from .accounts import (
    is_account_locked,
)


def select_chain(project):
    """
    Present the user with a prompt to select which of the project chains they
    want to use.
    """
    chain_options = set(project.config.chains.keys())

    choose_chain_msg = "\n".join(itertools.chain((
        "Available Chains",
        "----------------",
    ), (
        "{0} - {1}".format(chain_index, chain_name)
        for chain_index, chain_name in enumerate(sorted(chain_options))
    ), (
        "",
        "Enter ether the name, or number of the desired chain"
    )))
    chain_name = click.prompt(choose_chain_msg)
    if chain_name in chain_options:
        return chain_name
    elif chain_name.isdigit() and int(chain_name) < len(chain_options):
        return sorted(chain_options)[int(chain_name)]
    else:
        raise click.ClickException(
            "Invalid choice: {0}.  Please choose from one of the "
            "provided options.".format(chain_name)
        )


def select_account(chain):
    """
    Present the user with a prompt to select which of the chain accounts they
    would like to use.
    """
    all_accounts = chain.web3.eth.accounts
    if not all_accounts:
        raise click.ClickException("No accounts found on chain.")
    unlocked_accounts = {
        account for account in all_accounts
        if not is_account_locked(chain.web3, account)
    }

    pick_account_message = '\n'.join(itertools.chain((
        "Accounts",
        "-----------------",
    ), (
        "{index} - {account}{extra}".format(
            account=account,
            extra=" (unlocked)" if account in unlocked_accounts else "",
            index=index,
        ) for (index, account) in enumerate(all_accounts)
    ), (
        "",
        "Enter the account address or the number of the desired account",
    )))

    account_choice = click.prompt(
        pick_account_message,
        default=chain.web3.eth.defaultAccount,
    )

    if account_choice in set(all_accounts):
        return account_choice
    elif account_choice.isdigit() and int(account_choice) < len(all_accounts):
        return all_accounts[int(account_choice)]
    else:
        raise click.ClickException(
            "Invalid choice: {0}.  Please choose from one of the "
            "provided options.".format(account_choice)
        )


def configure_chain(project, chain_name):
    """
    Interactive configuration of an existing or new chain.

    - is it external?
    - rpc or ipc?
    - rpc/ipc configuration
    - select default account (web3.eth.defaultAccount)
    """
    is_existing_chain = chain_name in project.config.chains

    chain_section_header = "chain:{chain_name}".format(chain_name=chain_name)

    if is_existing_chain:
        chain_config = dict(project.config.items(chain_section_header))
    else:
        chain_config = {}

    start_msg = "Configuring {status} chain: {chain_name}".format(
        status="existing" if is_existing_chain else "**new**",
        chain_name=chain_name,
    )
    click.echo(start_msg)
    click.echo('-' * len(start_msg))

    if is_existing_chain:
        current_configuration_msg = "\n".join(itertools.chain((
            "Current Configuration",
        ), (
            "  {key} = {value}".format(key=key, value=value)
            for key, value in chain_config.items()
        )))
        click.echo(current_configuration_msg)

    # Internal or External
    internal_or_external_msg = (
        "\n\nPopulus can run the blockchain client for you, including "
        "connecting to the public main and test networks.\n\n "
        "Should populus manage running this chain?"
    )
    is_internal = click.confirm(internal_or_external_msg, default=True)

    if not is_internal:
        chain_config['is_external'] = 'True'

    # Web3 Provider
    web3_provider_msg = (
        "\n\nWeb3 Provider Choices:\n"
        "1) IPC socket (default)\n"
        "2) RPC via HTTP\n\n"
        "How should populus connect web3.py to this chain?"
    )
    provider = click.prompt(web3_provider_msg, default='ipc')

    if provider.lower() in {'ipc', '1'}:
        chain_config['provider'] = 'web3.providers.ipc.IPCProvider'
    elif provider.lower() in {'rpc', '2'}:
        chain_config['provider'] = 'web3.providers.rpc.RPCProvider'
    else:
        unknown_provider_message = (
            "Invalid response.  Allowed responses are 1/2/ipc/rpc"
        )
        raise click.ClickException(unknown_provider_message)

    if chain_config['provider'] == 'web3.providers.ipc.IPCProvider':
        custom_ipc_path_msg = (
            "\n\nWill this blockchain be running with a non-standard `geth.ipc`"
            "path?\n\n"
        )
        if click.confirm(custom_ipc_path_msg, default=False):
            ipc_path_msg = "Path to `geth.ipc` socket?"
            ipc_path = click.prompt(ipc_path_msg)
            chain_config['ipc_path'] = ipc_path
    elif chain_config['provider'] == 'web3.providers.rpc.RPCProvider':
        custom_rpc_host = (
            "\n\nWill the RPC server be bound to `localhost`?"
        )
        if not click.confirm(custom_rpc_host, default=True):
            rpc_host_msg = "Hostname?"
            rpc_host = click.prompt(rpc_host_msg)
            chain_config['rpc_host'] = rpc_host

        custom_rpc_port = (
            "\n\nWill the RPC server be listening on port 8545?"
        )
        if not click.confirm(custom_rpc_port, default=True):
            rpc_port_msg = "Port?"
            rpc_port = click.prompt(rpc_port_msg)
            chain_config['rpc_port'] = rpc_port

    if not project.config.has_section(chain_section_header):
        project.config.add_section(chain_section_header)

    # Save config so that we can spin this chain up.
    for key, value in chain_config.items():
        project.config.set(chain_section_header, key, value)

    project.write_config()

    if project.config.chains[chain_name].get('is_external', False):
        is_chain_ready_msg = (
            "Populus needs to connect to the chain.  Press [Enter] when the "
            "chain is ready for populus"
        )
        click.confirm(is_chain_ready_msg)

    with project.get_chain(chain_name) as chain:
        web3 = chain.web3
        choose_default_account_msg = (
            "This chain will default to sending transactions from "
            "{0}.  Would you like to set a different default "
            "account?".format(web3.eth.defaultAccount)
        )
        if click.confirm(choose_default_account_msg):
            default_account = select_account(chain)
            project.config.set(
                chain_section_header, 'default_account', default_account,
            )

    click.echo(
        "Writing configuration to {0} ...".format(project.primary_config_file_path)
    )
    project.write_config()
    click.echo("Success!")


def request_account_unlock(chain, account, timeout):
    """
    Present a password prompt to unlock the given account.
    """
    if not is_account_locked(chain.web3, account):
        raise click.ClickException(
            "The account `{0}` is already unlocked".format(account)
        )

    unlock_account_msg = (
        "Please provide the password to unlock account `{0}`.".format(account)
    )
    unlock_successful = chain.web3.personal.unlockAccount(
        account,
        click.prompt(unlock_account_msg, hide_input=True),
        timeout,
    )
    if not unlock_successful:
        raise click.ClickException("Unable to unlock account: `{0}`".format(account))


def deploy_contract_and_verify(chain,
                               contract_name,
                               base_contract_factory=None,
                               deploy_transaction=None,
                               deploy_arguments=None,
                               link_dependencies=None):
    """
    This is a *loose* wrapper around `populus.utils.deploy.deploy_contract`
    that handles the various concerns and logging that need to be present when
    doing this as a CLI interaction.

    Deploy a contract, displaying information about the deploy process as it
    happens.  This also verifies that the deployed contract's bytecode matches
    the expected value.
    """
    if link_dependencies is None:
        link_dependencies = {}

    web3 = chain.web3

    if base_contract_factory is None:
        base_contract_factory = chain.contract_factories[contract_name]

    if is_account_locked(web3, web3.eth.defaultAccount):
        deploy_from = select_account(chain)
        if is_account_locked(web3, deploy_from):
            request_account_unlock(chain, deploy_from, None)

    # TODO: this needs to do contract linking.
    click.echo("Deploying {0}".format(contract_name))

    deploy_txn_hash, contract_factory = deploy_contract(
        chain=chain,
        contract_name=contract_name,
        contract_factory=base_contract_factory,
        deploy_transaction=deploy_transaction,
        deploy_arguments=deploy_arguments,
        link_dependencies=link_dependencies,
    )
    deploy_txn = web3.eth.getTransaction(deploy_txn_hash)

    click.echo("Deploy Transaction Sent: {0}".format(deploy_txn_hash))
    click.echo("Waiting for confirmation...")

    contract_address = chain.wait.for_contract_address(
        deploy_txn_hash,
        timeout=180,
    )
    deploy_receipt = web3.eth.getTransactionReceipt(deploy_txn_hash)

    click.echo((
        "\n"
        "Transaction Mined\n"
        "=================\n"
        "Tx Hash      : {0}\n"
        "Address      : {1}\n"
        "Gas Provided : {2}\n"
        "Gas Used     : {3}\n\n".format(
            deploy_txn_hash,
            contract_address,
            deploy_txn['gas'],
            deploy_receipt['gasUsed'],
        )
    ))

    # Verification
    deployed_code = web3.eth.getCode(contract_address)

    if contract_factory.code_runtime:
        click.echo("Verifying deployed bytecode...")
        is_bytecode_match = deployed_code == contract_factory.code_runtime
        if is_bytecode_match:
            click.echo(
                "Verified contract bytecode @ {0} matches expected runtime "
                "bytecode".format(contract_address)
            )
        else:
            click.echo(
                "Bytecode @ {0} does not match expected contract bytecode.\n\n"
                "expected : '{1}'\n"
                "actual   : '{2}'\n".format(
                    contract_address,
                    contract_factory.code_runtime,
                    deployed_code,
                ),
                err=True,
            )
            raise click.ClickException("Error deploying contract")
    else:
        click.echo(
            "No runtime available.  Falling back to verifying non-empty "
            "bytecode."
        )
        if len(deployed_code) <= 2:
            click.echo(
                "Bytecode @ {0} is unexpectedly empty.".format(contract_address),
                err=True,
            )
            raise click.ClickException("Error deploying contract")
        else:
            click.echo(
                "Verified bytecode @ {0} is non-empty".format(contract_address)
            )
    return contract_factory(address=contract_address)


def show_chain_sync_progress(chain):
    """
    Display the syncing status of a chain as a progress bar
    """
    web3 = chain.web3

    if not web3.net.peerCount:
        click.echo("Waiting for peer connections.")
        try:
            chain.wait.for_peers(timeout=240)
        except gevent.Timeout:
            raise click.ClickException("Never connected to any peers.")

    if not web3.eth.syncing:
        click.echo("Waiting for synchronization to start.")
        try:
            chain.wait.for_syncing(timeout=240)
        except gevent.Timeout:
            raise click.ClickException("Chain synchronization never started.")

    starting_block = web3.eth.syncing['startingBlock']

    while True:
        sync_data = web3.eth.syncing

        if not sync_data:
            break

        highest_block = sync_data['highestBlock']
        blocks_to_sync = highest_block - starting_block

        with click.progressbar(length=blocks_to_sync, label="Syncing") as bar:

            while highest_block == sync_data['highestBlock']:
                sync_data = web3.eth.syncing

                if not sync_data:
                    break

                current_block = sync_data['currentBlock']
                blocks_to_sync = highest_block - starting_block

                position = current_block - starting_block

                if position:
                    bar.update(position)

                if current_block >= highest_block:
                    break

                gevent.sleep(random.random())
            else:
                # start a new progress bar with the new `highestBlock`
                continue

            # break out of the outer loop
            break


def get_unlocked_deploy_from_address(chain):
    """
    Combination of other utils to get the address deployments should come from.

    Defaults to the one set in the config.
    If not set, asks for one.
    If not in config, asks if it should be set as default.
    If not unlocked, askes for password to unlock.
    """
    web3 = chain.web3
    chain_config = chain.chain_config
    chain_name = chain.chain_name
    chain_section_name = "chain:{name}".format(name=chain_name)
    project = chain.project
    config = project.config

    # Choose the address we should deploy from.
    if 'deploy_from' in chain_config:
        account = chain_config['deploy_from']
        if account not in web3.eth.accounts:
            raise click.ClickException(
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
            if not config.has_section(chain_section_name):
                config.add_section(chain_section_name)
            config.set(chain_section_name, 'deploy_from', account)
            click.echo(
                "Wrote updated chain configuration to '{0}'".format(project.write_config())
            )

    # Unlock the account if needed.
    if is_account_locked(web3, account):
        try:
            # in case the chain is still spinning up, give it a moment to
            # unlock itself.
            chain.wait.for_unlock(account, timeout=5)
        except gevent.Timeout:
            request_account_unlock(chain, account, None)

    return account


def compile_project_contracts(project, optimize=True):
    click.echo("============ Compiling ==============")
    click.echo("> Loading source files from: ./{0}\n".format(project.contracts_dir))

    result = compile_and_write_contracts(
        project.project_dir,
        project.contracts_dir,
        optimize=optimize
    )
    contract_source_paths, compiled_sources, output_file_path = result

    click.echo("> Found {0} contract source files".format(
        len(contract_source_paths)
    ))
    for path in contract_source_paths:
        click.echo("- {0}".format(os.path.relpath(path)))
    click.echo("")
    click.echo("> Compiled {0} contracts".format(len(compiled_sources)))

    for contract_name in sorted(compiled_sources.keys()):
        click.echo("- {0}".format(contract_name))

    click.echo("")
    click.echo(
        "> Wrote compiled assets to: ./{0}".format(
            os.path.relpath(output_file_path)
        )
    )


def watch_project_contracts(project, **compile_kwargs):
    watcher = DirWatcher(project.contracts_dir)

    last_hash = project.get_source_file_hash()

    try:
        while True:
            event = watcher.get()
            if event.name in {'update', 'add', 'create'}:
                current_hash = project.get_source_file_hash()
                if current_hash == last_hash:
                    continue
                last_hash = current_hash
                click.echo("Change detected in: {e.path}".format(e=event))
                compile_project_contracts(project, **compile_kwargs)
    except KeyboardInterrupt:
        pass


def select_project_contract(project):
    contract_names = sorted(project.compiled_contracts.keys())
    contract_choices = [
        " {idx}: {name}".format(
            idx=str(idx).rjust(3),
            name=name,
        ) for idx, name
        in enumerate(contract_names)
    ]
    select_contract_message = (
        "Please select the desired contract:\n\n"
        "{0}".format(
            '\n'.join(contract_choices)
        )
    )
    contract_name = click.prompt(select_contract_message)
    if contract_name in project.compiled_contracts:
        return contract_name
    elif contract_name.isdigit() and int(contract_name) < len(contract_names):
        return contract_names[int(contract_name)]
    else:
        bad_choice_message = (
            "'{0}' is not a valid choice.  Please enter either the numeric "
            "index of the desired contract or the full name of the "
            "contract.".format(
                contract_name,
            )
        )
        raise click.ClickException(bad_choice_message)
