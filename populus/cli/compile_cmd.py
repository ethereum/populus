import click
import warnings

from populus.utils.cli import (
    watch_project_contracts,
)
from populus.utils.compat import (
    spawn,
)

from populus.api.compile_contracts import (
    compile_project_dir,
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
    user_config_path = ctx.obj['user_config_path']

    project = compile_project_dir(project_root_dir, user_config_path)

    if watch:
        warnings.warn("Watch will be deprecated in the next version of Populus", DeprecationWarning)
        thread = spawn(
            watch_project_contracts,
            project=project,
        )
        thread.join()
