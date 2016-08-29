import sys

import click

from populus.utils.filesystem import (
    is_same_path,
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
    '--config',
    '-c',
    help=(
        "Specify a populus configuration file to be used.  No other "
        "configuration files will be loaded"
    ),
    type=click.File(),
    multiple=True,
)
@click.pass_context
def main(ctx, config):
    """
    Populus
    """
    project = Project(config)

    if not any(is_same_path(p, project.project_dir) for p in sys.path):
        # ensure that the project directory is in the sys.path
        sys.path.insert(0, project.project_dir)

    ctx.obj = {}
    ctx.obj['PROJECT'] = project
