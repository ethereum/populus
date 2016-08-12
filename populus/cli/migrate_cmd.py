import itertools
import click

from populus.utils.transactions import (
    get_contract_address_from_txn,
    is_account_locked,
)
from populus.utils.cli import (
    select_chain,
)

from .main import main


@main.group(
    'migrate',
    invoke_without_command=True,
)
@click.pass_context
def migrate(ctx):
    """
    Run project migrations
    """
    if ctx.invoked_subcommand is None:
        click.echo("Invoked migration command")
        # run the migrations
        pass


@migrate.command('init')
@click.pass_context
def migrate_init(ctx):
    """
    Prepare the current chain for migrations.

    contract onto this chain as well as
    """
    project = ctx.obj['PROJECT']

    # First determine which chain should be used.
    if 'CHAIN_NAME' in ctx.obj:
        chain_name = ctx['CHAIN_NAME']
    else:
        chain_name = select_chain(project)

    if chain_name == 'testrpc':
        ctx.abort("Cannot initialize the {0!r} chain".format(chain_name))

    if not project.config.has_section("chain:{0}".format(chain_name)):
        project.config.add_section("chain:{0}".format(chain_name))

    with project.get_chain(chain_name) as chain:
        web3 = chain.web3

        # TODO: Check syncing status here:
        syncing = web3.eth.syncing
        if syncing:
            ctx.abort(str(syncing))

        if not web3.eth.accounts:
            # TODO: we can actually create a new account for the user.
            no_accounts_msg = (
                "There are no accounts on this chain. Once you have created an "
                "account, you can initialize the migrations."
            )
            ctx.abort(no_accounts_msg)

        if 'registrar' not in chain.chain_config:
            if is_account_locked(web3, web3.eth.defaultAccount):
                unlock_message = (
                    "In order to initialize the chain populus needs to deploy the "
                    "Registrar contract which requires an unlocked account.  Populus "
                    "will do this for you if you will provide the password for the "
                    "account {0!r}.  The account will be unlocked for 5 seconds."
                    "".format(
                        web3.eth.defaultAccount,
                    )
                )
                account_password = click.prompt(unlock_message, hide_input=True)
                unlock_successful = web3.personal.unlockAccount(
                    web3.eth.defaultAccount,
                    account_password,
                    5,
                )
                if not unlock_successful:
                    ctx.abort("Unable to unlock account.")

            RegistrarFactory = chain.RegistrarFactory
            deploy_txn_hash = RegistrarFactory.deploy()

            click.echo("Deployed Registrar contract via txn: {0}".format(
                deploy_txn_hash,
            ))
            registrar_address = get_contract_address_from_txn(
                web3=web3,
                txn_hash=deploy_txn_hash,
                timeout=180,
            )

            deployed_code = web3.eth.getCode(registrar_address)
            if deployed_code != RegistrarFactory.code_runtime:
                registrar_deploy_failed_msg = (
                    "Something appears to have gone wrong during deployment. "
                    "The code for the deployed registrar contract does not match "
                    "the expected runtime bytecode."
                    "\n"
                    "expected: {0!r}\n"
                    "actual: {1!r}".format(
                        RegistrarFactory.code_runtime,
                        deployed_code,
                    )
                )
                ctx.abort(registrar_deploy_failed_msg)

            project.config.set(
                'chain:{0}'.format(chain_name),
                'registrar',
                registrar_address,
            )
            with open(ctx.obj['PRIMARY_CONFIG'], 'w') as config_file:
                project.config.write(config_file)

            click.echo("Wrote updated configuration to {0!r}".format(
                ctx.obj['PRIMARY_CONFIG'],
            ))
        else:
            click.echo("Looks like this chain already has a registrar")
