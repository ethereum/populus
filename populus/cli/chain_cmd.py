import random
import functools

import gevent
import click

from populus.utils.filesystem import (
    ensure_path_exists,
)
from populus.utils.cli import (
    select_chain,
    configure_chain,
    deploy_contract_and_verify,
    show_chain_sync_progress,
    get_unlocked_default_account_address,
)
from populus.chain import (
    BaseGethChain,
    reset_chain,
)

from .main import main


@main.group('chain')
@click.pass_context
def chain_cmd(ctx):
    """
    Manage and run ethereum blockchains.
    """
    pass


@chain_cmd.command('reset')
@click.argument('chain_name', nargs=1, default="default")
@click.option('--confirm/--no-confirm', default=True)
@click.pass_context
def chain_reset(ctx, chain_name, confirm):
    """
    Reset a chain removing all chain data and resetting it to it's genesis
    state..
    """
    project = ctx.obj['PROJECT']

    if confirm:
        confirmation_message = (
            "Are you sure you want to reset blockchain {0}: {1}".format(
                chain_name,
                project.get_blockchain_data_dir(chain_name),
            )
        )
        if not click.confirm(confirmation_message):
            raise ctx.abort()
    reset_chain(project.get_blockchain_data_dir(chain_name))


@chain_cmd.command('run')
@click.argument('chain_name', nargs=1, default="default")
@click.option('--mine/--no-mine', default=True)
@click.option(
    '--verbosity', default=5,
    help="""
    Set verbosity of the logging output. Default is 5, Range is 0-6.
    """)
@click.pass_context
def chain_run(ctx, chain_name, mine, verbosity):
    """
    Run the named chain.
    """
    project = ctx.obj['PROJECT']

    chain = project.get_chain(chain_name)

    if isinstance(chain, BaseGethChain):
        chain.geth.register_stdout_callback(click.echo)
        chain.geth.register_stderr_callback(functools.partial(click.echo, err=True))

    with chain:
        try:
            while True:
                gevent.sleep(random.random())
        except KeyboardInterrupt:
            pass


@chain_cmd.command('config')
@click.argument('chain_name', nargs=1)
@click.pass_context
def chain_configure(ctx, chain_name):
    """
    Configure a blockchain
    """
    project = ctx.obj['PROJECT']

    configure_chain(project, chain_name)


@chain_cmd.command('init')
@click.argument('chain_name', nargs=1, required=False)
@click.pass_context
def chain_init(ctx, chain_name):
    """
    Prepare the current chain for migrations.

    contract onto this chain as well as
    """
    project = ctx.obj['PROJECT']

    ensure_path_exists(project.migrations_dir)

    # Determine which chain should be used.
    if not chain_name:
        chain_name = select_chain(project)

    if chain_name in {'testrpc', 'tester', 'temp'}:
        ctx.abort("Cannot initialize the {0!r} chain".format(chain_name))

    if chain_name not in project.config['chains']:
        ctx.forward(chain_configure)

    chain = project.get_chain(chain_name)

    if not chain.has_registrar:
        # We need to deploy the registrar
        with chain:
            web3 = chain.web3

            if chain_name in {'mainnet', 'ropsten'}:
                show_chain_sync_progress(chain)

            web3.eth.defaultAccount = get_unlocked_default_account_address(chain)

            # Deploy the registrar
            RegistrarFactory = chain.RegistrarFactory
            registrar = deploy_contract_and_verify(chain,
                                                   contract_name='Registrar',
                                                   base_contract_factory=RegistrarFactory)

            # Write the registrar address to the chain config
            project.config['chains.{0}.registrar'.format(chain_name)] = registrar.address
            project.write_config()

            click.echo("Wrote updated chain configuration to")

    click.echo("The '{0}' blockchain is ready for migrations.".format(
        chain_name
    ))
