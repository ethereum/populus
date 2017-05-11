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
    V3,
    V4,
)


NEW_V4_PATHS = {
    'compilation.backends.SolcCombinedJSON',
    'compilation.backend',
    'compilation.import_remappings',
}

MOVED_V3_PATHS = {
    'compilation.settings': 'compilation.backends.SolcCombinedJSON.settings',
    'compilation.import_remapping': 'compilation.import_remappings',
}


def upgrade_v3_to_v4(v3_config):
    """
    Upgrade a v3 config file to a v4 config file.
    """
    errors = get_validation_errors(v3_config, version=V3)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v3_default_config = load_default_config(version=V3)
    v4_default_config = load_default_config(version=V4)

    if v3_config == v3_default_config:
        return v4_default_config

    upgraded_v3_config = copy.deepcopy(v3_config)

    for key_path in NEW_V4_PATHS:
        if has_nested_key(upgraded_v3_config, key_path):
            continue
        set_nested_key(
            upgraded_v3_config,
            key_path,
            get_nested_key(v4_default_config, key_path),
        )

    for old_path, new_path in MOVED_V3_PATHS.items():
        default_value = get_nested_key(v4_default_config, new_path)

        if has_nested_key(upgraded_v3_config, old_path):
            existing_value = pop_nested_key(upgraded_v3_config, old_path)

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
                upgraded_v3_config,
                new_path,
                merged_value,
            )
        else:
            set_nested_key(
                upgraded_v3_config,
                new_path,
                default_value,
            )

    # bump the version
    set_nested_key(upgraded_v3_config, 'version', V4)

    errors = get_validation_errors(upgraded_v3_config, version=V4)
    if errors:
        raise ValueError(
            "Upgraded configuration did not pass validation:\n\n"
            "\n=============Original-Configuration============\n"
            "{0}"
            "\n=============Upgraded-Configuration============\n"
            "{1}"
            "\n=============Validation-Errors============\n"
            "{2}".format(
                pprint.pformat(dict(v3_config)),
                pprint.pformat(dict(upgraded_v3_config)),
                format_errors(errors),
            )
        )

    return upgraded_v3_config
