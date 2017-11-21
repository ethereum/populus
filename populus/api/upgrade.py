import copy
import logging

from populus.config import (
    load_config,
    write_config,
)
from populus.config.upgrade import (
    upgrade_config as _upgrade_config,
    ConfigContext,
)
from populus.config.versions import (
    LATEST_VERSION,
    LAST_NO_USER_CONFIG_VERSION,
)

import shutil


logger = logging.getLogger('populus.api.upgrade')


# TODO: rename to something not so closely named as `populus.config.upgrade.upgrade_config`
def upgrade_configs(project_dir, to_version=None):
    """
    Performs an upgrade on the project and populus config files to the
    specified version (defaulting to the current latest version)
    """
    if to_version is None:
        to_version = LATEST_VERSION

    project_config_file_path = get_project_config_file_path(project_dir)
    # TODO: handle the config file not existing
    config_file_is_present = check_if_proj
    project_config = load_config(project_config_file_path)

    if int(populus_config['version']) < int(LATEST_VERSION):
        populus_config = upgrade_config(populus_config, ConfigContext.USER)
        write_config(populus_config, project.populus_config_file_path)

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
