from __future__ import absolute_import

import copy

from populus.utils.mappings import (
    set_nested_key,
    get_nested_key,
    has_nested_key,
    pop_nested_key,
)

from .defaults import (
    load_default_config,
)
from .validation import (
    validate_config,
)


NEW_V2_PATHS = {
    'contracts',
    'chains.mainnet.contracts',
    'chains.ropsten.contracts',
    'chains.temp.contracts',
    'chains.testrpc.contracts',
    'chains.tester.contracts',
}

V2_TRANSLATIONS = {
    'compilation.contracts_dir': 'compilation.contracts_source_dir',
}

V2_UPDATES = {
    'chains.mainnet.chain.class',
    'chains.ropsten.chain.class',
    'chains.temp.chain.class',
    'chains.testrpc.chain.class',
    'chains.tester.chain.class',
}


def upgrade_v1_to_v2(v1_config):
    """
    Upgrade a v1 config file to a v2 config file.
    """
    errors = validate_config(v1_config, version='1')
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                "\n- ".join(errors),
            )
        )

    v1_default_config = load_default_config(version='1')
    v2_default_config = load_default_config(version='2')

    if v1_config == v1_default_config:
        return v2_default_config

    upgraded_v1_config = copy.deepcopy(v1_config)

    for key_path in NEW_V2_PATHS:
        if has_nested_key(upgraded_v1_config, key_path):
            continue
        set_nested_key(
            upgraded_v1_config,
            key_path,
            get_nested_key(v2_default_config, key_path),
        )

    for old_path, new_path in V2_TRANSLATIONS.items():
        if not has_nested_key(upgraded_v1_config, old_path):
            continue
        set_nested_key(
            upgraded_v1_config,
            new_path,
            pop_nested_key(upgraded_v1_config, old_path),
        )

    for key_path in V2_UPDATES:
        if not has_nested_key(upgraded_v1_config, key_path):
            continue
        current_value = get_nested_key(upgraded_v1_config, key_path)
        old_default_value = get_nested_key(v1_default_config, key_path)

        if current_value == old_default_value:
            set_nested_key(
                upgraded_v1_config,
                key_path,
                get_nested_key(v2_default_config, key_path),
            )

    # bump the version
    set_nested_key(upgraded_v1_config, 'version', '2')

    validate_config(upgraded_v1_config, version='2')

    return upgraded_v1_config
