import click

from populus.config.helpers import (
    check_if_project_json_file_exists,
)

from populus.exceptions import (
    ConfigError,
)

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
    project_root_dir = ctx.obj['project_root_dir']
    user_config_path = ctx.obj['user_config_path']

    if check_if_project_json_file_exists(project_root_dir):
        raise ConfigError(
            "Project json config file already exists at {root_dir}, can not init new project".format(
                root_dir=project_root_dir
            )
        )

    init_project(project_root_dir, user_config_path)
