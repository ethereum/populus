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
    '--config',
    '-c',
    'config_file_path',
    help=(
        "Specify a populus configuration file to be used.  No other "
        "configuration files will be loaded"
    ),
    type=click.Path(exists=True, dir_okay=False),
)
@click.pass_context
def main(ctx, config_file_path):
    """
    Populus
    """

    logger = get_logger_with_click_handler('populus')

    ctx.obj = {}
    ctx.obj['PROJECT'] = "project"
