from populus.config.defaults import (
    load_default_config,
)
from populus.config.upgrade import (
    upgrade_v1_to_v2,
)


def test_default_config_upgrade():
    v1_default_config = load_default_config(version='1')
    v2_default_config = load_default_config(version='2')

    upgraded_v1_config = upgrade_v1_to_v2(v1_default_config)
    assert upgraded_v1_config == v2_default_config
