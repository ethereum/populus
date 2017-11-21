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


REF_KEYS = (
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
        _upgrade_v7_to_v8(v7_populus_config, v7_default_populus, v8_default_populus)

    v7_default_project = load_default_project_config(version=V7)
    v8_default_project = load_default_populus_config(version=V8)
    _upgrade_v7_to_v8(v7_project_config, v7_default_project, v8_default_project)


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


def _upgrade_v7_to_v8(v7_config, v7_default, v8_default):
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

    # TODO: remove the unreffing
    v7_default_config = Config(v7_default)
    v7_default_config.unref()

    v8_default_config = Config(v8_default)

    if v7_config == v7_default_config:
        populus_config_file_path = get_populus_config_file_path()
        backup_file_path = "{0}.{1}.backup".format(
            populus_config_file_path,
            int(time.time()),
        )
        shutil.copy(populus_config_file_path, backup_file_path)
        os.remove(populus_config_file_path)
        return None
        return v8_default_config

    # V8 just moved to user config, no change in keys
    upgraded_v7_config = copy.deepcopy(v7_config)
    upgraded_v7_config['version'] = V8

    for key in REF_KEYS:
        default_value = get_nested_key(v7_default_config)

        if not has_nested_key(v7_config, key):
            set_nested_key(upgraded_v7_config, key, default_value)
            continue

        current_value = get_nested_key(v7_config, key)

        if current_value == default_value:
            set_nested_key(upgraded_v7_config, key, default_value)
        elif _is_ref(current_value):
            ref_value = current_value['$ref']

            if has_nested_key(v7_config, ref_value):
                resolved_ref_value = get_nested_key(v7_config, ref_value)
                set_nested_key(upgraded_v7_config, key, resolved_ref_value)
            else:
                raise ValueError(
                    "Unable to upgrade to v8 configuration.  Found reference "
                    "under the key `{0}` but unable to resolve the referenced "
                    "path {1}".format(key, ref_value)
                )
        else:
            # this case just leaves the key the same as it's currently set.
            pass
            set_nested_key(upgraded_v7_config, key, current_value)

    return upgraded_v7_config
