from __future__ import absolute_import

import itertools
import logging

import click

from populus.compilation import (
    compile_project_contracts,
)

from .accounts import (
    is_account_locked,
)
from .compat import (
    Timeout,
    sleep,
)
from .compile import (
    write_compiled_sources,
)
from .contracts import (
    verify_contract_bytecode,
)

from .observers import (
    DirWatcher,
)

from web3.utils.empty import (
    Empty,
)


def select_chain(project):
    """
    Present the user with a prompt to select which of the project chains they
    want to use.
    """
    chain_options = set(project.config['chains'].keys())

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

    pick_account_message = '\n'.join(itertools.chain((
        "Accounts",
        "-----------------",
    ), (
        "{index} - {account}".format(
            account=account,
            index=index,
        ) for (index, account) in enumerate(all_accounts)
    ), (
        "",
        "Enter the account address or the number of the desired account",
    )))

    account_choice = click.prompt(
        pick_account_message,
        default=chain.web3.eth.defaultAccount or chain.web3.eth.coinbase,
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

    # default="" is for allowing empty password
    unlock_successful = chain.web3.personal.unlockAccount(
        account,
        click.prompt(unlock_account_msg, hide_input=True, default=""),
        timeout,
    )
    if not unlock_successful:
        raise click.ClickException("Unable to unlock account: `{0}`".format(account))


def deploy_contract_and_verify(chain,
                               contract_name,
                               ContractFactory=None,
                               deploy_transaction=None,
                               deploy_args=None,
                               deploy_kwargs=None):
    """
    This is a *loose* wrapper around `populus.utils.deploy.deploy_contract`
    that handles the various concerns and logging that need to be present when
    doing this as a CLI interaction.

    Deploy a contract, displaying information about the deploy process as it
    happens.  This also verifies that the deployed contract's bytecode matches
    the expected value.
    """
    web3 = chain.web3
    logger = logging.getLogger('populus.utils.cli.deploy_contract_and_verify')

    if isinstance(web3.eth.defaultAccount, Empty):
        # must have coinbase
        # TODO: add --account arg (index or address), and set default account here if provided
        web3.eth.defaultAccount = web3.eth.coinbase

    if is_account_locked(web3, web3.eth.defaultAccount):
        try:
            chain.wait.for_unlock(web3.eth.defaultAccount or web3.eth.coinbase, 5)
        except Timeout:
            default_account = select_account(chain)
            if is_account_locked(web3, default_account):
                request_account_unlock(chain, default_account, None)
            web3.eth.defaultAccount = default_account

    logger.info("Deploying {0}".format(contract_name))

    if ContractFactory is None:
        ContractFactory = chain.provider.get_contract_factory(contract_name)

    deploy_txn_hash = ContractFactory.deploy(
        transaction=deploy_transaction,
        args=deploy_args,
        kwargs=deploy_kwargs,
    )
    deploy_txn = web3.eth.getTransaction(deploy_txn_hash)

    logger.info("Deploy Transaction Sent: {0}".format(deploy_txn_hash))
    logger.info("Waiting for confirmation...")

    contract_address = chain.wait.for_contract_address(
        deploy_txn_hash,
        timeout=180,
    )
    deploy_receipt = web3.eth.getTransactionReceipt(deploy_txn_hash)

    logger.info((
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
    deployed_bytecode = web3.eth.getCode(contract_address)

    if ContractFactory.bytecode_runtime:
        verify_contract_bytecode(web3, ContractFactory.bytecode_runtime, contract_address)
        logger.info("Verified contract bytecode @ {0}".format(contract_address))
    else:
        logger.info(
            "No runtime available.  Falling back to verifying non-empty "
            "bytecode."
        )
        if len(deployed_bytecode) <= 2:
            logger.error("Bytecode @ {0} is unexpectedly empty.".format(contract_address))
            raise click.ClickException("Error deploying contract")
        else:
            logger.info(
                "Verified bytecode @ {0} is non-empty".format(contract_address)
            )
    return ContractFactory(address=contract_address)


def watch_project_contracts(project, compiler_settings):
    logger = logging.getLogger('populus.utils.cli.watch_project_contracts')

    def callback(file_path, event_name):
        if event_name in {'modified', 'created'}:
            logger.info("============ Compiling ==============")
            logger.info("> Change detected in: %s", file_path)
            for source_dir in project.contracts_source_dirs:
                logger.info("> Loading source files from: %s", source_dir)

            contract_source_paths, compiled_sources = compile_project_contracts(project)
            write_compiled_sources(
                project.compiled_contracts_asset_path,
                compiled_sources,
            )

            logger.info("> Watching ...")

    watcher = DirWatcher(project.contracts_dir, callback)
    watcher.start()

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass


def select_project_contract(project):
    contract_names = sorted(project.compiled_contract_data.keys())
    contract_choices = [
        " {idx}: {name}".format(
            idx=str(idx).rjust(3),
            name=name,
        ) for idx, name
        in enumerate(contract_names)
    ]
    select_contract_message = (
        "Please select the desired contract:\n\n"
        "{0}\n\n".format(
            '\n'.join(contract_choices)
        )
    )
    contract_name = click.prompt(select_contract_message)
    if contract_name in project.compiled_contract_data:
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
