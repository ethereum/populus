from __future__ import absolute_import

from .defaults import (
    load_default_config,
)


def upgrade_v1_to_v2(v1_config):
    v1_default_config = load_default_config(version='1')
    v2_default_config = load_default_config(version='2')

    if v1_config == v1_default_config:
        return v2_default_config
    raise NotImplementedError("Not yet implemented: durr")
