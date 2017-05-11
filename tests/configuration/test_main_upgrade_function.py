import pytest

import itertools

from populus.config import (
    Config,
)
from populus.config.defaults import (
    load_default_config,
)
from populus.config.upgrade import (
    upgrade_config,
)
from populus.config.validation import (
    load_config_schema,
)
from populus.config.versions import (
    V1,
    V2,
    V3,
    V4,
)


@pytest.mark.parametrize(
    'from_to_version,use_config_object',
    tuple(itertools.product(
        (
            (V1, V2),
            (V1, V3),
            (V1, V4),
            (V2, V3),
            (V2, V4),
            (V3, V4),
        ),
        (True, False),
    )),
)
def test_default_config_upgrade(from_to_version, use_config_object):
    from_version, to_version = from_to_version
    base_initial_config = load_default_config(version=from_version)
    expected_config = load_default_config(version=to_version)

    if use_config_object:
        config_schema = load_config_schema(version=from_version)
        initial_config = Config(base_initial_config, schema=config_schema)
    else:
        initial_config = base_initial_config

    upgraded_config = upgrade_config(initial_config, to_version=to_version)
    assert upgraded_config == expected_config
