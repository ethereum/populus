from populus.config.upgrade import (
    upgrade_project_config,
)
from populus.config.versions import (
    V7,
    V8,
)
from populus.utils.testing import (
    project_config_version,
)


@project_config_version(V7)
def test_stock_v7_to_v8_upgrade(project):
    assert project.project_config['version'] == V7

    upgrade_project_config(project.project_dir)

    project.reload_config()
    assert project.project_config['version'] == V8
