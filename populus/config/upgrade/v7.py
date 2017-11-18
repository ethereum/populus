
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
    V7,
    V8,
)

from populus.config import (
    Config,
)


def upgrade_v7_to_v8(v7_config):
    """
    Upgrade a v7 config file to a v8 config file.
    """
    errors = get_validation_errors(v7_config, version=V7)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v7_default = load_default_config(version=V7)
    v8_default = load_default_config(version=V8)

    # TODO: remove the unreffing
    v7_default_config = Config(v7_default)
    v7_default_config.unref()

    v8_default_config = Config(v8_default)
    v8_default_config.unref()

    if v7_config == v7_default_config:
        return v8_default_config

    # V8 just moved to user config, no change in keys
    upgraded_v7_config = copy.deepcopy(v7_config)
    upgraded_v7_config['version'] = V8

    return upgraded_v7_config
