import gevent

import click

from populus.utils.cli import (
    compile_project_contracts,
    watch_project_contracts,
)

from .main import main


@main.command('compile')
@click.option(
    '--watch',
    '-w',
    is_flag=True,
    help="Watch contract source files and recompile on changes",
)
@click.option(
    '--optimize',
    '-o',
    default=True,
    is_flag=True,
    help="Enable compile time optimization",
)
@click.pass_context
def compile_contracts(ctx, watch, optimize):
    """
    Compile project contracts, storing their output in `./build/contracts.json`

    Call bare to compile all contracts or specify contract names or file paths
    to restrict to only compiling those contracts.

    Pass in a file path and a contract name separated by a colon(":") to
    specify only named contracts in the specified file.
    """
    project = ctx.obj['PROJECT']

    compile_project_contracts(project, optimize=True)

    if watch:
        thread = gevent.spawn(
            watch_project_contracts,
            project=project,
            optimize=True,
        )
        thread.join()
