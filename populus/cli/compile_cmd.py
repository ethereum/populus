import click
import os

from populus.api.compile import (
    compile
)

from .main import main


@main.command('compile')
@click.option(
    '--project-root',
    '-p',
    help="The project root direcetory",
)
@click.pass_context
def compile_cmd(ctx, project_root):
    """
    Compile project contracts, storing their output in `./build/contracts.json`

    Call bare to compile all contracts or specify contract names or file paths
    to restrict to only compiling those contracts.

    Pass in a file path and a contract name separated by a colon(":") to
    specify only named contracts in the specified file.
    """

    if project_root is None:
        project_root = os.getcwd()

    compile(project_root_dir=project_root)


