from __future__ import absolute_import

import copy
import pprint

from populus.utils.mappings import (
    set_nested_key,
    get_nested_key,
    has_nested_key,
)

from populus.config.defaults import (
    load_default_config,
)
from populus.config.validation import (
    get_validation_errors,
    format_errors,
)
from populus.config.versions import (
    V2,
    V3,
)


NEW_V3_PATHS = {
    'chains.mainnet.contracts.backends.TestContracts',
    'chains.ropsten.contracts.backends.TestContracts',
    'chains.temp.contracts.backends.TestContracts',
    'chains.testrpc.contracts.backends.TestContracts',
    'chains.tester.contracts.backends.TestContracts',
    'contracts.backends.TestContracts',
}


def upgrade_v2_to_v3(v2_config):
    """
    Upgrade a v2 config file to a v3 config file.
    """
    errors = get_validation_errors(v2_config, version=V2)
    if errors:
        raise ValueError(
            "Cannot upgrade invalid config.  Please ensure that your current "
            "configuration file is valid:\n\n{0}".format(
                format_errors(errors),
            )
        )

    v2_default_config = load_default_config(version=V2)
    v3_default_config = load_default_config(version=V3)

    if v2_config == v2_default_config:
        return v3_default_config

    upgraded_v2_config = copy.deepcopy(v2_config)

    for key_path in NEW_V3_PATHS:
        if has_nested_key(upgraded_v2_config, key_path):
            continue
        set_nested_key(
            upgraded_v2_config,
            key_path,
            get_nested_key(v3_default_config, key_path),
        )

    # bump the version
    set_nested_key(upgraded_v2_config, 'version', V3)

    errors = get_validation_errors(upgraded_v2_config, version=V3)
    if errors:
        raise ValueError(
            "Upgraded configuration did not pass validation:\n\n"
            "\n=============Original-Configuration============\n"
            "{0}"
            "\n=============Upgraded-Configuration============\n"
            "{1}"
            "\n=============Validation-Errors============\n"
            "{2}".format(
                pprint.pformat(dict(v2_config)),
                pprint.pformat(dict(upgraded_v2_config)),
                format_errors(errors),
            )
        )

    return upgraded_v2_config
