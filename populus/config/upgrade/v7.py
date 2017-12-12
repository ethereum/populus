from __future__ import absolute_import

import copy

from populus.config.defaults import (
    load_default_config,
    load_user_default_config,
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

    v7_default_config = Config(v7_default)

    if v7_config == v7_default_config:
        return {}

    # V8 just removes all of the `$ref` values from the config.
    upgraded_v7_config = Config(copy.deepcopy(v7_config))
    upgraded_v7_config.unref()
    upgraded_v7_config['version'] = V8

    return upgraded_v7_config


def upgrade_user_v7_to_v8(v7_user_config):
    """
    Upgrade a v7 user config file to a v8 user config file.
    """
    errors = get_validation_errors(v7_user_config, version=V7)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v7_default = load_user_default_config(version=V7)

    v7_default_config = Config(v7_default)

    if v7_user_config == v7_default_config:
        return {}

    # V8 just removes all of the `$ref` values from the config.
    upgraded_v7_user_config = Config(copy.deepcopy(v7_user_config))
    upgraded_v7_user_config.unref()
    upgraded_v7_user_config['version'] = V8

    return upgraded_v7_user_config
