import os
import click

from populus.utils.config import (
    load_config,
    get_config_paths,
    PRIMARY_CONFIG_FILENAME,
)
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
    if not config:
        primary_config = os.path.join(project_dir, PRIMARY_CONFIG_FILENAME)
        config = get_config_paths(project_dir)
    else:
        primary_config = config[0]

    project = Project(load_config(config), chain=chain)

    ctx.obj = {}
    ctx.obj['PROJECT'] = project
    ctx.obj['PRIMARY_CONFIG'] = primary_config
