from __future__ import absolute_import

import copy
import pprint

from eth_utils import (
    is_string,
)

from populus.utils.mappings import (
    set_nested_key,
    get_nested_key,
    has_nested_key,
    pop_nested_key,
)

from populus.config.defaults import (
    load_default_config,
)
from populus.config.validation import (
    get_validation_errors,
    format_errors,
)
from populus.config.versions import (
    V5,
    V6,
)


NEW_V6_PATHS = {
    'compilation.backends.SolcStandardJSON.settings.stdin',
}


def upgrade_v5_to_v6(v5_config):
    """
    Upgrade a v5 config file to a v6 config file.
    """
    errors = get_validation_errors(v5_config, version=V5)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v5_default_config = load_default_config(version=V5)
    v6_default_config = load_default_config(version=V6)

    if v5_config == v5_default_config:
        return v6_default_config

    upgraded_v5_config = copy.deepcopy(v5_config)

    # new configuration values whos keys were not present in the previous
    # configuration.
    for key_path in NEW_V6_PATHS:
        if has_nested_key(upgraded_v5_config, key_path):
            continue
        set_nested_key(
            upgraded_v5_config,
            key_path,
            get_nested_key(v6_default_config, key_path),
        )

    if has_nested_key(upgraded_v5_config, 'compilation.contracts_source_dir'):
        current_contracts_source_dir = pop_nested_key(
            upgraded_v5_config,
            'compilation.contracts_source_dir',
        )
        if is_string(current_contracts_source_dir):
            contract_source_dirs = [current_contracts_source_dir]
        else:
            contract_source_dirs = current_contracts_source_dir
        set_nested_key(
            upgraded_v5_config,
            'compilation.contract_source_dirs',
            contract_source_dirs,
        )

    # bump the version
    set_nested_key(upgraded_v5_config, 'version', V6)

    errors = get_validation_errors(upgraded_v5_config, version=V6)
    if errors:
        raise ValueError(
            "Upgraded configuration did not pass validation:\n\n"
            "\n=============Original-Configuration============\n"
            "{0}"
            "\n=============Upgraded-Configuration============\n"
            "{1}"
            "\n=============Validation-Errors============\n"
            "{2}".format(
                pprint.pformat(dict(v5_config)),
                pprint.pformat(dict(upgraded_v5_config)),
                format_errors(errors),
            )
        )

    return upgraded_v5_config
