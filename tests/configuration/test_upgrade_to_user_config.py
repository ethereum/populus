import logging
import os
import pytest
import shutil

from populus.config import (
    Config,
    load_config,
)

from populus.config.loading import (
    write_config,
)

from populus.config.defaults import (
    load_default_config,
    load_user_default_config,
    get_default_config_path,
)

from populus.config.helpers import (
    get_legacy_json_config_file_path,
)

from populus.project import (
    Project,
)

from populus.config.versions import (
    V1,
    V2,
    V3,
    V4,
    V5,
    V6,
    V8,
    V9,
    LATEST_VERSION,
)

from populus.api.upgrade import (
    upgrade_configs,
)

from populus.utils.testing import (
    user_config_version,
)


@pytest.mark.parametrize(
    'from_legacy_version',
    (V1, V2, V3, V4, V5, V6)
)
@user_config_version(V9)
def test_upgrade_to_user_config(project, from_legacy_version):

    shutil.copyfile(
        get_default_config_path(version=from_legacy_version),
        get_legacy_json_config_file_path(project_dir=project.project_dir)
    )

    logger = logging.getLogger("test.test_upgrade_to_user_config")
    upgrade_configs(project.project_dir, logger, LATEST_VERSION)

    upgraded_project = Project(
        project_dir=project.project_dir,
        user_config_file_path=project.user_config_file_path
    )

    expected_user_config = Config(load_user_default_config(LATEST_VERSION))
    expected_user_config.unref()

    expected_project_config = Config(load_default_config(LATEST_VERSION))
    expected_project_config.unref()

    legacy_config_path = get_legacy_json_config_file_path(project.project_dir)
    assert not os.path.exists(legacy_config_path)

    assert upgraded_project.user_config == expected_user_config
    assert upgraded_project.project_config == expected_project_config


@user_config_version(V9)
def test_upgrade_custom_key(project):
    legacy_config_file_path = get_legacy_json_config_file_path(project_dir=project.project_dir)
    shutil.copyfile(
        get_default_config_path(version=V3),
        legacy_config_file_path
    )

    legacy_key = 'compilation.import_remapping'
    legacy_value = ['import-path-from-legacy=contracts']
    upgraded_key = 'compilation.import_remappings'

    legacy_config = Config(load_config(legacy_config_file_path))
    legacy_config[legacy_key] = legacy_value
    write_config(legacy_config, legacy_config_file_path)

    logger = logging.getLogger("test.test_upgrade_custom_key")
    upgrade_configs(project.project_dir, logger, V8)

    upgraded_project = Project(
        project_dir=project.project_dir,
        user_config_file_path=project.user_config_file_path
    )

    assert upgraded_project.config.get(upgraded_key) == legacy_value
    assert upgraded_project.project_config.get(upgraded_key) == legacy_value

    default_user_config = Config(load_user_default_config(version=V9))
    assert upgraded_project.user_config.get(upgraded_key) == default_user_config.get(upgraded_key)
