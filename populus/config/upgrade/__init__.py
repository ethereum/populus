from __future__ import absolute_import

import pprint

from toolz.functoolz import (
    pipe,
)

from eth_utils import (
    to_tuple,
)

from populus.config.versions import (
    V1,
    V2,
    V3,
    V4,
    V5,
    KNOWN_VERSIONS,
    LATEST_VERSION,
)
from .v1 import upgrade_v1_to_v2
from .v2 import upgrade_v2_to_v3
from .v3 import upgrade_v3_to_v4
from .v4 import upgrade_v4_to_v5


UPGRADE_SEQUENCE = {
    V1: V2,
    V2: V3,
    V3: V4,
    V4: V5,
}
UPGRADE_FUNCTIONS = {
    V1: upgrade_v1_to_v2,
    V2: upgrade_v2_to_v3,
    V3: upgrade_v3_to_v4,
    V4: upgrade_v4_to_v5,
}


@to_tuple
def get_upgrade_sequence(start_version, end_version):
    if start_version not in KNOWN_VERSIONS:
        raise KeyError("Unknown version '{0}':  Must be one of '{1}'".format(
            start_version,
            ', '.join(sorted(KNOWN_VERSIONS)),
        ))
    elif end_version not in KNOWN_VERSIONS:
        raise KeyError("Unknown version '{0}':  Must be one of '{1}'".format(
            end_version,
            ', '.join(sorted(KNOWN_VERSIONS)),
        ))
    elif start_version == end_version:
        raise ValueError("Config is already at version: '{0}'".format(end_version))

    elif int(start_version) > int(end_version):
        raise ValueError("Cannot downgrade config from version '{0}' to '{1}'".format(
            start_version,
            end_version,
        ))

    current_version = start_version
    while current_version != end_version:
        yield current_version
        current_version = UPGRADE_SEQUENCE[current_version]


def upgrade_config(config, to_version=LATEST_VERSION):
    try:
        current_version = config['version']
    except KeyError:
        raise KeyError("No version key found in config file:\n\n{0}".format(
            pprint.pformat(config),
        ))

    upgrade_sequence = get_upgrade_sequence(current_version, to_version)
    upgrade_functions = tuple(
        UPGRADE_FUNCTIONS[version] for version in upgrade_sequence
    )
    upgraded_config = pipe(config, *upgrade_functions)
    return upgraded_config
