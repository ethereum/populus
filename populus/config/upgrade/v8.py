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
    V8,
    V9,
)

from populus.config import (
    Config,
)


def upgrade_v8_to_v9(v8_config):
    """
    Upgrade a v8 config file to a v9 config file.
    """
    errors = get_validation_errors(v8_config, version=V8)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v8_default = load_default_config(version=V8)

    v8_default_config = Config(v8_default)

    if v8_config == v8_default_config:
        return {}

    # V9 just removes all of the `$ref` values from the config.
    upgraded_v8_config = Config(copy.deepcopy(v8_config))
    upgraded_v8_config.unref()
    upgraded_v8_config['version'] = V9

    return upgraded_v8_config


def upgrade_user_v8_to_v9(v8_user_config):
    """
    Upgrade a v8 user config file to a v9 user config file.
    """
    errors = get_validation_errors(v8_user_config, version=V8)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v8_default = load_user_default_config(version=V8)

    v8_default_config = Config(v8_default)

    if v8_user_config == v8_default_config:
        return {}

    # V9 just removes all of the `$ref` values from the config.
    upgraded_v8_user_config = Config(copy.deepcopy(v8_user_config))
    upgraded_v8_user_config.unref()
    upgraded_v8_user_config['version'] = V9

    return upgraded_v8_user_config
