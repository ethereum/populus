from __future__ import absolute_import
import enum
import pprint

from cytoolz.functoolz import (
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
    V6,
    V7,
    KNOWN_LEGACY_VERSIONS,
    KNOWN_USER_VERSIONS,
    LATEST_VERSION,
)
from .v1 import upgrade_v1_to_v2
from .v2 import upgrade_v2_to_v3
from .v3 import upgrade_v3_to_v4
from .v4 import upgrade_v4_to_v5
from .v5 import upgrade_v5_to_v6
from .v6 import upgrade_v6_to_v7


UPGRADE_SEQUENCE = {
    V1: V2,
    V2: V3,
    V3: V4,
    V4: V5,
    V5: V6,
    V6: V7,
}

UPGRADE_FUNCTIONS = {
    V1: upgrade_v1_to_v2,
    V2: upgrade_v2_to_v3,
    V3: upgrade_v3_to_v4,
    V4: upgrade_v4_to_v5,
    V5: upgrade_v5_to_v6,
    V6: upgrade_v6_to_v7,
}


class ConfigContext(enum.Enum):
    USER = 1
    LEGACY = 2


@to_tuple
def get_upgrade_sequence(start_version, end_version, known_versions):

    if start_version not in known_versions:
        raise KeyError("Unknown version '{0}':  Must be one of '{1}'".format(
            start_version,
            ', '.join(sorted(known_versions)),
        ))
    elif end_version not in known_versions:
        raise KeyError("Unknown version '{0}':  Must be one of '{1}'".format(
            end_version,
            ', '.join(sorted(known_versions)),
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


def upgrade_config(config, config_context, to_version=LATEST_VERSION):

    if config_context == ConfigContext.USER:
        known_versions = KNOWN_USER_VERSIONS
    elif config_context == ConfigContext.LEGACY:
        known_versions = KNOWN_LEGACY_VERSIONS

    try:
        current_version = config['version']
    except KeyError:
        raise KeyError("No version key found in config file:\n\n{0}".format(
            pprint.pformat(config),
        ))

    upgrade_sequence = get_upgrade_sequence(current_version, to_version, known_versions)
    upgrade_functions = tuple(
        UPGRADE_FUNCTIONS[version] for version in upgrade_sequence
    )
    upgraded_config = pipe(config, *upgrade_functions)
    return upgraded_config
