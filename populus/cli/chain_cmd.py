import random
import functools

import click

from populus.chain import (
    BaseGethChain,
    reset_chain,
)
from populus.utils.compat import (
    sleep,
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
                sleep(random.random())
        except KeyboardInterrupt:
            pass
