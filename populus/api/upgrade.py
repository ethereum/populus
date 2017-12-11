import os

from populus.config import (
    load_config,
    write_config,
)

from populus.config.upgrade import (
    upgrade_config,
    upgrade_user_config,
    ConfigContext,
)

from populus.config.versions import (
    LATEST_VERSION,
)
from populus.config.helpers import (
    get_user_json_config_file_path,
    get_json_config_file_path,
)


def upgrade_configs(project_dir, logger, to_version):
    """upgrade project and the user config file"""

    user_config_file_path = get_user_json_config_file_path()
    if os.path.exists(user_config_file_path):
        user_config = load_config(user_config_file_path)
        current_user_config_version = int(user_config['version'])

        if current_user_config_version < int(LATEST_VERSION):
            upgraded_user_config = upgrade_user_config(user_config, to_version)
            if upgrade_config:
                write_config(upgraded_user_config, user_config_file_path)
            else:
                os.remove(user_config_file_path)

    project_config_file_path = get_json_config_file_path(project_dir)
    if os.path.exists(project_config_file_path):
        project_config = load_config(project_config_file_path)
        project_config_version = int(project_config['version'])

        if project_config_version < int(LATEST_VERSION):
            upgraded_project_config = upgrade_config(
                project_config,
                ConfigContext.USER,
                to_version,
            )
            if upgraded_project_config:
                write_config(upgraded_project_config, project_config_file_path)
            else:
                os.path.remove(upgraded_project_config)
