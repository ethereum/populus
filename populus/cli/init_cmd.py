import logging
import click
from .main import main

from populus.api.project import (
    init_project,
)


@main.command('init')
@click.pass_context
def init_cmd(ctx):
    """
    Generate project layout with an example contract.
    """
    logger = logging.getLogger('populus.cli.init_cmd')
    project_dir = ctx.obj['PROJECT_DIR']

    init_project(project_dir, logger)
