import click
import warnings

from populus.utils.cli import (
    watch_project_contracts,
)
from populus.utils.compat import (
    spawn,
)

from populus.api.compile import (
    compile,
)

from .main import main


@main.command('compile')
@click.option(
    '--watch',
    '-w',
    is_flag=True,
    help="Watch contract source files and recompile on changes",
)
@click.pass_context
def compile_cmd(ctx, watch):
    """
    Compile project contracts, storing their output in `./build/contracts.json`

    Call bare to compile all contracts or specify contract names or file paths
    to restrict to only compiling those contracts.

    Pass in a file path and a contract name separated by a colon(":") to
    specify only named contracts in the specified file.
    """
    project_root_dir = ctx.obj['project_root_dir']
    project = compile(project_root_dir)

    if watch:
        warnings.warn("Watch will be deprecated in the next version of Populus", DeprecationWarning)
        thread = spawn(
            watch_project_contracts,
            project=project,
        )
        thread.join()
