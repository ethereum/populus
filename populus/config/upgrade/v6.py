from __future__ import absolute_import

import copy

from populus.config.defaults import (
    load_default_config,
)

from populus.config.validation import (
    get_validation_errors,
    format_errors,
)

from populus.config.versions import (
    V6,
    V7,
)

from populus.config import (
    Config,
)


def upgrade_v6_to_v7(v6_config):
    """
    Upgrade a v6 config file to a v7 config file.
    """
    errors = get_validation_errors(v6_config, version=V6)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v6_default = load_default_config(version=V6)
    v7_default = load_default_config(version=V7)

    v6_default_config = Config(v6_default)
    v6_default_config.unref()

    v7_default_config = Config(v7_default)
    v7_default_config.unref()

    if v6_config == v6_default_config:
        return v7_default_config

    # V7 just moved to user config, no change in keys
    upgraded_v6_config = copy.deepcopy(v6_config)
    upgraded_v6_config['version'] = V7

    return upgraded_v6_config
