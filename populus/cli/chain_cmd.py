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
<<<<<<< HEAD
@click.option(
    '--active/--no-active', default=True,
    help="""
    Set whether the chain run will modify the active-chain settings.
    Default is to modify the active-chain setting.
    """)
@click.option(
     '--rpccorsdomain', default=None,
     help="""
     Determines the value that will be passed in as the `--rpcorsdomain` to the `geth` instance.
     """)
def chain_run(name, mine, verbosity, active, rpccorsdomain):
=======
def chain_run(name, mine, verbosity):
>>>>>>> upstream/master
    """
    Run a geth node.
    """
    project_dir = os.getcwd()
<<<<<<< HEAD
    data_dir = get_geth_data_dir(project_dir, name)
    logfile_path = get_geth_logfile_path(data_dir)

    ensure_account_exists(data_dir)

    kwargs = {
#        "logfile": logfile_path,
        "verbosity": "%d" % verbosity,
        "rpccorsdomain": 'http://localhost:5000'
        }

    command, proc = run_geth_node(data_dir, mine=mine,  **kwargs)

    click.echo("Running: '{0}'".format(' '.join(command)))

    if active:
        set_active_data_dir(project_dir, name)

    try:
        while True:
            out_line = proc.get_stdout_nowait()
            if out_line:
                click.echo(out_line, nl=False)

            err_line = proc.get_stderr_nowait()
            if err_line:
                click.echo(err_line, nl=False)

            if err_line is None and out_line is None:
                time.sleep(0.2)
    except KeyboardInterrupt:
=======

    with dev_geth_process(project_dir, name):
>>>>>>> upstream/master
        try:
            while True:
                gevent.sleep(0)
        except KeyboardInterrupt:
            pass
