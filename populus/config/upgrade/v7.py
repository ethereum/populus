from __future__ import absolute_import

import copy
import os
import shutil
import time

from eth_utils import (
    is_dict,
    is_string,
)

from populus.config.helpers import (
    get_populus_config_file_path,
    load_default_project_config,
    load_default_populus_config,
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
from populus.utils.mappings import (
    get_nested_key,
    has_nested_key,
    set_nested_key,
)


KEYS_TO_DEREFERENCE = (
    "chains.mainnet.web3",
    "chains.mainnet.contracts.backends.JSONFile",
    "chains.mainnet.contracts.backends.Memory",
    "chains.mainnet.contracts.backends.ProjectContracts",
    "chains.mainnet.contracts.backends.TestContracts",
    "chains.ropsten.web3",
    "chains.ropsten.contracts.backends.JSONFile",
    "chains.ropsten.contracts.backends.Memory",
    "chains.ropsten.contracts.backends.ProjectContracts",
    "chains.ropsten.contracts.backends.TestContracts",
    "chains.temp.web3",
    "chains.ropsten.contracts.backends.Memory",
    "chains.ropsten.contracts.backends.ProjectContracts",
    "chains.ropsten.contracts.backends.TestContracts",
    "chains.tester.web3",
    "chains.ropsten.contracts.backends.Memory",
    "chains.ropsten.contracts.backends.ProjectContracts",
    "chains.ropsten.contracts.backends.TestContracts",
    "chains.testrpc.web3",
    "chains.ropsten.contracts.backends.Memory",
    "chains.ropsten.contracts.backends.ProjectContracts",
    "chains.ropsten.contracts.backends.TestContracts",
    "compilation.backend"
)


REMOVED_KEYS = {
    "compilation.backends.SolcCombinedJSON",
}


def upgrade_v7_to_v8(v7_project_config, v7_populus_config):
    v7_default_populus = load_default_populus_config(version=V7)
    v8_default_populus = load_default_populus_config(version=V8)

    # In the v7 to v8 upgrade, populus changed from having it's default populus
    # config file written into the home directory to just using a baked in
    # version within the populus codebase.  In the case where the populus
    # config is the same as the default, we can just remove it.
    if v7_populus_config == v7_default_populus:
        populus_config_file_path = get_populus_config_file_path()
        backup_file_path = "{0}.{1}.backup".format(
            populus_config_file_path,
            int(time.time()),
        )
        shutil.copy(populus_config_file_path, backup_file_path)
        os.remove(populus_config_file_path)
    else:
        _perform_v7_to_v8_upgrade(v7_populus_config, v7_default_populus, v8_default_populus)

    v7_default_project = load_default_project_config(version=V7)
    v8_default_project = load_default_populus_config(version=V8)

    if v7_project_config == v7_default_project:
        return v8_default_project
    else:
        _perform_v7_to_v8_upgrade(v7_project_config, v7_default_project, v8_default_project)


def _is_ref(value):
    if not is_dict(value):
        return False

    keys = set(value.keys())
    if keys != {"$ref"}:
        return

    ref_value = value['$ref']

    if not is_string(ref_value):
        return False

    return True


def _perform_v7_to_v8_upgrade(v7_config, v7_default, v8_default):
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

    v7_default_config = Config(v7_default)
    v8_default_config = Config(v8_default)

    # V8 just moved to user config, no change in keys
    upgraded_v7_config = copy.deepcopy(v7_config)
    upgraded_v7_config['version'] = V8

    for key in KEYS_TO_DEREFERENCE:
        default_v7_value = get_nested_key(v7_default_config)
        default_v8_value = get_nested_key(v8_default_config)

        if not has_nested_key(v7_config, key):
            set_nested_key(upgraded_v7_config, key, default_v8_value)
            continue

        current_value = get_nested_key(v7_config, key)

        if current_value == default_v7_value:
            set_nested_key(upgraded_v7_config, key, default_v8_value)
        elif _is_ref(current_value):
            ref_value = current_value['$ref']

            if has_nested_key(v7_config, ref_value):
                # If it is a reference **and** the reference exists, replace it
                # with referenced value.
                resolved_ref_value = get_nested_key(v7_config, ref_value)
                set_nested_key(upgraded_v7_config, key, resolved_ref_value)
            else:
                raise ValueError(
                    "Unable to upgrade to v8 configuration.  Found reference "
                    "under the key `{0}` but unable to resolve the referenced "
                    "path {1}".format(key, ref_value)
                )
        else:
            # If it's not the default and it's not a reference we just want to
            # retain the previous value.
            pass

    return upgraded_v7_config
