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
    KNOWN_USER_VERSIONS,
    LAST_NO_USER_CONFIG_VERSION,
)
from populus.config.helpers import (
    get_user_json_config_file_path,
    get_json_config_file_path,
    get_legacy_json_config_file_path,
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

    legacy_config_file_path = get_legacy_json_config_file_path(project_dir)
    project_config_file_path = get_json_config_file_path(project_dir)

    if os.path.exists(legacy_config_file_path):
        legacy_config = load_config(legacy_config_file_path)
        legacy_version = legacy_config['version']

        if int(legacy_version) > int(LAST_NO_USER_CONFIG_VERSION):
            raise KeyError(
                "Unkown legacy version {legacy_version} at {legacy_config}".format(
                    legacy_version=legacy_version,
                    legacy_config=legacy_config
                )
            )
        elif int(legacy_version) < int(LAST_NO_USER_CONFIG_VERSION):
            upgraded_legacy_config = upgrade_config(
                legacy_config,
                ConfigContext.LEGACY,
                LAST_NO_USER_CONFIG_VERSION
            )
            write_config(upgraded_legacy_config, legacy_config_file_path)

    has_project_config = os.path.exists(project_config_file_path)
    has_legacy_config = os.path.exists(legacy_config_file_path)

    if has_project_config or has_legacy_config:
        if has_project_config:
            project_config = load_config(project_config_file_path)
        elif has_legacy_config:
            project_config = load_config(legacy_config_file_path)
        else:
            raise Exception("Invariant")
        project_config_version = int(project_config['version'])

        if project_config_version < int(LATEST_VERSION):
            upgraded_project_config = upgrade_config(
                project_config,
                ConfigContext.USER,
                to_version,
            )
            if upgraded_project_config:
                write_config(upgraded_project_config, project_config_file_path)
            elif has_project_config:
                os.remove(project_config_file_path)

    if os.path.exists(legacy_config_file_path) and to_version in KNOWN_USER_VERSIONS:
        os.rename(
            legacy_config_file_path,
            "{0}.backup".format(legacy_config_file_path),
        )
