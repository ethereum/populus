import logging
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


def validate_logging_level(ctx, param, value):
    normalized_value = value.lower()
    if normalized_value.lower() in {'info', '20'}:
        return logging.INFO
    elif normalized_value.lower() in {'debug', '10'}:
        return logging.DEBUG
    else:
        raise click.BadParameter(
            "Logging level must be one of DEBUG/INFO or the numeric equivalents "
            "10/20"
        )


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--project',
    '-p',
    'project_dir',
    help=(
        "Specify a populus project directory"
    ),
    type=click.Path(exists=True, dir_okay=True),
)
@click.option(
    '--logging',
    '-l',
    'logging_level',
    help=(
        "Specify the logging level.  Allowed values are DEBUG/INFO or their "
        "numeric equivalents 10/20"
    ),
    default=str(logging.INFO),
    callback=validate_logging_level,
)
@click.pass_context
def main(ctx, project_dir, logging_level):
    """
    Populus
    """
    logger = get_logger_with_click_handler('populus', level=logging_level)
    ctx.obj = {}
    ctx.obj['PROJECT_DIR'] = project_dir

    if ctx.invoked_subcommand not in ('init', 'upgrade'):

        project = Project(project_dir)

        config_version = project.config['version']
        subcommand_bypasses_config_version = ctx.invoked_subcommand in {'config'}

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

        ctx.obj['PROJECT'] = project
