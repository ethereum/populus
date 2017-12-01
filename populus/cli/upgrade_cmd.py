import click
from .main import main

from populus.api.upgrade import (
    do_config_upgrade,
)

from populus.config.versions import (
    LATEST_VERSION,
)


@main.command('upgrade')
@click.pass_context
@click.option(
    '-t',
    '--to-version',
    'to_version',
    default=LATEST_VERSION,
)
def upgrade_cmd(ctx, to_version):
    """
    Upgrade a project config, and if required also the user config
    Note: the user config is used in other projects as well
    """
    project_dir = ctx.obj['PROJECT_DIR']

    do_config_upgrade(project_dir)
