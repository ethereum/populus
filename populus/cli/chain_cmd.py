import os

import gevent
import click

from populus.utils.chains import (
    get_data_dir,
)
from populus.chain import (
    reset_chain,
    dev_geth_process,
)

from .main import main


@main.group()
@click.pass_context
def chain(ctx):
    """
    Wrapper around `geth`.
    """
    pass


@chain.command('reset')
@click.argument('chain_name', nargs=1, default="default")
@click.option('--confirm/--no-confirm', default=True)
@click.pass_context
def chain_reset(ctx, chain_name, confirm):
    """
    Reset a test chain
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


@chain.command('run')
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
    Run a geth node.
    """
    project = ctx.obj['PROJECT']

    chain = project.get_chain(chain_name)

    with chain:
        try:
            while True:
                gevent.sleep(0)
        except KeyboardInterrupt:
            pass
