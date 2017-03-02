import os
import sys
import warnings

import click

from populus.utils.filesystem import (
    is_same_path,
)
from populus.project import (
    Project,
)
from populus.legacy.config import (
    upgrade_legacy_config_file,
    check_if_ini_config_file_exists,
)
from populus.config.versions import (
    LATEST_VERSION,
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
    if not config_file_path and check_if_ini_config_file_exists():
        click.echo("Attempting to upgrade legacy `populus.ini` config file")
        try:
            backup_ini_config_file_path = upgrade_legacy_config_file(os.getcwd())
        except:
            click.echo(
                "The following error occured while trying to upgrade the legacy "
                "`populus.ini` config file:"
            )
            raise
        else:
            click.echo(
                "Project configuration upgraded.  New config file "
                "`populus.json` has been written.  Old config file was renamed "
                "to `{0}`".format(backup_ini_config_file_path)
            )

    project = Project(config_file_path)

    config_version = project.config['version']
    if config_version != LATEST_VERSION:
        warnings.warn(DeprecationWarning(
            "Your populus config file is current at version {0}. "
            "The current version is {1}.  You can use the `populus config "
            "upgrade` command to upgrade your config file to the latest version"
        ))

    if not any(is_same_path(p, project.project_dir) for p in sys.path):
        # ensure that the project directory is in the sys.path
        sys.path.insert(0, project.project_dir)

    ctx.obj = {}
    ctx.obj['PROJECT'] = project
