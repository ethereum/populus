import os

import gevent
import click

from populus.utils.chain import (
    get_data_dir,
)
from populus.chain import (
    reset_chain,
    dev_geth_process,
)

from .main import main


@main.group()
def chain():
    """
    Wrapper around `geth`.
    """
    pass


@chain.command('reset')
@click.argument('name', nargs=1, default="default")
@click.option('--confirm/--no-confirm', default=True)
def chain_reset(name, confirm):
    """
    Reset a test chain
    """
    # TODO: from `main` command
    project_dir = os.getcwd()
    data_dir = get_data_dir(project_dir, name)
    if confirm:
        confirmation_message = (
            "Are you sure you want to reset blockchain {0}: {1}".format(
                name,
                data_dir,
            )
        )
        if not click.confirm(confirmation_message):
            raise click.Abort()
    reset_chain(data_dir)


@chain.command('run')
@click.argument('name', nargs=1, default="default")
@click.option('--mine/--no-mine', default=True)
@click.option(
    '--verbosity', default=5,
    help="""
    Set verbosity of the logging output. Default is 5, Range is 0-6.
    """)
def chain_run(name, mine, verbosity):
    """
    Run a geth node.
    """
    project_dir = os.getcwd()
    with dev_geth_process(project_dir, name):
        try:
            while True:
                gevent.sleep(0)
        except KeyboardInterrupt:
            pass
