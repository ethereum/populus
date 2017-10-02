import copy
from populus.config import (
    load_config,
    write_config,
)

from populus.config.upgrade import (
    upgrade_config,
    ConfigContext,
)

from populus.project import (
    Project,
)

from populus.config.versions import (
    LATEST_VERSION,
    LAST_NO_USER_CONFIG_VERSION,
)

import shutil


def upgrade_configs(project_dir, logger, to_version=None):
    """upgrade project and the user config file"""

    project = Project(project_dir=project_dir, create_config_file=True)

    if to_version is None:
        to_version = LATEST_VERSION

    user_config = copy.deepcopy(project.user_config)
    if int(user_config['version']) < int(LATEST_VERSION):
        user_config = upgrade_config(user_config, ConfigContext.USER)
        write_config(user_config, project.user_config_file_path)

    if project.legacy_config_path is not None:

        legacy_config = load_config(project.legacy_config_path)
        legacy_version = legacy_config['version']
        if int(legacy_version) > int(LAST_NO_USER_CONFIG_VERSION):
            raise KeyError(
                "Unkown legacy version {legacy_version} at {legacy_config}".format(
                    legacy_version=legacy_version,
                    legacy_config=legacy_config
                )
            )
        elif int(legacy_version) < int(LAST_NO_USER_CONFIG_VERSION):
            legacy_config = upgrade_config(
                legacy_config, ConfigContext.LEGACY, LAST_NO_USER_CONFIG_VERSION
            )

        shutil.move(
            project.legacy_config_path,
            project.legacy_config_path + ".orig"
        )
        write_config(legacy_config, project.config_file_path)
        project.reload_config()

    project_config = copy.deepcopy(project.project_config)
    if int(project_config['version']) < int(LATEST_VERSION):
        project_config = upgrade_config(project_config, ConfigContext.USER)
        write_config(project_config, project.config_file_path)

    project.reload_config()
    project.clean_config()
