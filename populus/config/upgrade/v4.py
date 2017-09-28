from __future__ import absolute_import

import copy
import itertools
import pprint

from eth_utils import (
    is_dict,
    is_list_like,
)

from populus.utils.mappings import (
    set_nested_key,
    get_nested_key,
    has_nested_key,
    pop_nested_key,
    deep_merge_dicts,
)

from populus.config.defaults import (
    load_default_config,
)
from populus.config.validation import (
    get_validation_errors,
    format_errors,
)
from populus.config.versions import (
    V4,
    V5,
)


NEW_V5_PATHS = {
    'compilation.backends.SolcAutoBackend',
    'compilation.backends.SolcStandardJSON',
}

MOVED_V4_PATHS = {
}

MODIFIED_V4_PATHS = {
    'compilation.backends.SolcCombinedJSON.settings.output_values',
}


def upgrade_v4_to_v5(v4_config):
    """
    Upgrade a v4 config file to a v5 config file.
    """
    errors = get_validation_errors(v4_config, version=V4)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v4_default_config = load_default_config(version=V4)
    v5_default_config = load_default_config(version=V5)

    if v4_config == v4_default_config:
        return v5_default_config

    upgraded_v4_config = copy.deepcopy(v4_config)

    # new configuration values whos keys were not present in the previous
    # configuration.
    for key_path in NEW_V5_PATHS:
        if has_nested_key(upgraded_v4_config, key_path):
            continue
        set_nested_key(
            upgraded_v4_config,
            key_path,
            get_nested_key(v5_default_config, key_path),
        )

    # keys in the new configuration that were relocated.
    for old_path, new_path in MOVED_V4_PATHS.items():
        default_value = get_nested_key(v5_default_config, new_path)

        if has_nested_key(upgraded_v4_config, old_path):
            existing_value = pop_nested_key(upgraded_v4_config, old_path)

            if is_dict(default_value) and is_dict(existing_value):
                merged_value = deep_merge_dicts(default_value, existing_value)
            elif is_list_like(default_value) and is_list_like(existing_value):
                merged_value = list(set(itertools.chain(default_value, existing_value)))
            else:
                raise ValueError(
                    "Unable to merge {0} with {1}".format(
                        type(default_value),
                        type(existing_value),
                    )
                )

            set_nested_key(
                upgraded_v4_config,
                new_path,
                merged_value,
            )
        else:
            set_nested_key(
                upgraded_v4_config,
                new_path,
                default_value,
            )

    # keys from the previous configuration that were changed.
    for key_path in MODIFIED_V4_PATHS:
        new_default = get_nested_key(v5_default_config, key_path)
        if key_path not in upgraded_v4_config:
            set_nested_key(
                upgraded_v4_config,
                key_path,
                new_default,
            )
        else:
            current_value = get_nested_key(upgraded_v4_config, key_path)
            old_default = get_nested_key(v4_default_config, key_path)
            if current_value == old_default:
                set_nested_key(
                    upgraded_v4_config,
                    key_path,
                    new_default,
                )

    # bump the version
    set_nested_key(upgraded_v4_config, 'version', V5)

    errors = get_validation_errors(upgraded_v4_config, version=V5)
    if errors:
        raise ValueError(
            "Upgraded configuration did not pass validation:\n\n"
            "\n=============Original-Configuration============\n"
            "{0}"
            "\n=============Upgraded-Configuration============\n"
            "{1}"
            "\n=============Validation-Errors============\n"
            "{2}".format(
                pprint.pformat(dict(v4_config)),
                pprint.pformat(dict(upgraded_v4_config)),
                format_errors(errors),
            )
        )

    return upgraded_v4_config
