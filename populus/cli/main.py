import sys
import warnings

import click

from populus.utils.filesystem import (
    is_same_path,
)
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

    project = Project(config_file_path)

    config_version = project.config['version']
    subcommand_bypasses_config_version = ctx.invoked_subcommand in {'config', 'init'}

    if not subcommand_bypasses_config_version and config_version != LATEST_VERSION:
        old_config_version_msg = (
            "================ warning =================\n"
            "Your populus config file is current at version {0}. "
            "The latest version is {1}.  You can use the `populus config "
            "upgrade` command to upgrade your config file to the latest version\n"
            "================ warning =================\n\n".format(
                config_version,
                LATEST_VERSION,
            )
        )
        warnings.warn(DeprecationWarning(old_config_version_msg))
        logger.warning(old_config_version_msg)
        proceed_msg = (
            "Without and up-to-date configuration file Populus may not function "
            "correctly.  Would you still like to proceed?"
        )
        if not click.confirm(proceed_msg):
            ctx.exit(1)

    if not any(is_same_path(p, project.project_dir) for p in sys.path):
        # ensure that the project directory is in the sys.path
        sys.path.insert(0, project.project_dir)

    ctx.obj = {}
    ctx.obj['PROJECT'] = project
