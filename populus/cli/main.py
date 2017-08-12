import os
import sys
import warnings

import click

from populus.project import (
    Project,
)
from populus.config.versions import (
    LATEST_VERSION,
)

from populus.utils.logging import (
    get_logger_with_click_handler,
)


CONTEXT_SETTINGS = dict(
    # Support -h as a shortcut for --help
    help_option_names=['-h', '--help'],
)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--project-root-dir',
    '-p',
    'project_root_dir',
    help=(
        "Specify a populus configuration file to be used.  No other "
        "configuration files will be loaded"
    ),
    type=click.Path(exists=True),
)
@click.option(
    '--warnings',
    'show_warnings',
    help=(
        "Show all warnings"
    ),
    default=False,
    is_flag=True
)
@click.pass_context
def main(ctx, project_root_dir,show_warnings):
    """
    Populus
    """
    logger = get_logger_with_click_handler('populus')
    if project_root_dir is None:
        project_root_dir = os.getcwd()
    ctx.obj = {}
    ctx.obj['project_root_dir'] = project_root_dir
    if show_warnings:
        warnings.filterwarnings("always")