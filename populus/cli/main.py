import os
import click

from populus.project import (
    Project,
)


CONTEXT_SETTINGS = dict(
    # Support -h as a shortcut for --help
    help_option_names=['-h', '--help'],
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--project-dir',
    '-p',
    help=(
        "Specify the root directory of the populus project.  Defaults to the "
        "current working directory"
    ),
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd,
)
@click.option(
    '--config',
    '-c',
    help=(
        "Specify a populus configuration file to be used.  No other "
        "configuration files will be loaded"
    ),
    type=click.File(),
    multiple=True,
)
@click.option(
    '--chain',
    '-b',
    help=(
        "Specifies that the project should be configured against a specific "
        "chain.  'mainnet' and 'morden' can be used as pre-defined public "
        "networks.  Other values should be predefined in your populus.ini"
    ),
)
@click.pass_context
def main(ctx, config, project_dir, chain):
    """
    Populus
    """
    project = Project(config)

    ctx.obj = {}
    ctx.obj['PROJECT'] = project

    if chain is not None:
        ctx.obj['CHAIN_NAME'] = chain
