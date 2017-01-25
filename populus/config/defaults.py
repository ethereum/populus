import os
import copy

import anyconfig

from populus import ASSETS_DIR

from populus.utils.functional import (
    cast_return_to_tuple,
)
from populus.utils.chains import (
    get_default_ipc_path as get_geth_default_ipc_path,
)
from populus.utils.config import (
    get_nested_key,
    has_nested_key,
    set_nested_key,
    resolve_config,
)


def set_geth_mainnet_ipc_path(config):
    set_nested_key(
        config,
        'provider.settings.ipc_path',
        get_geth_default_ipc_path(testnet=False),
    )
    return config


def set_geth_ropsten_ipc_path(config):
    set_nested_key(
        config,
        'provider.settings.ipc_path',
        get_geth_default_ipc_path(testnet=True),
    )
    return config


POPULUS_CONFIG_DEFAULTS = {
    #
    # Compilation
    #
    ('compilation', anyconfig.MS_DICTS),
    #
    # Chains
    #
    # Temp Geth Chains
    ('chains.temp.web3',),
    ('chains.temp.chain',),
    # Mainnet
    ('chains.mainnet.web3',),
    ('chains.mainnet.chain',),
    # Ropsten
    ('chains.ropsten.web3',),
    ('chains.ropsten.chain',),
    # TestRPC
    ('chains.testrpc.web3',),
    ('chains.testrpc.chain',),
    # Tester
    ('chains.tester.web3',),
    ('chains.tester.chain',),
    #
    # Web3 Presets
    #
    ('web3.InfuraRopsten',),
    ('web3.InfuraMainnet',),
    (
        'web3.GethMainnet',
        anyconfig.MS_NO_REPLACE,
        set_geth_mainnet_ipc_path,
    ),
    (
        'web3.GethRopsten',
        anyconfig.MS_NO_REPLACE,
        set_geth_ropsten_ipc_path,
    ),
    ('web3.GethEphemeral',),
    ('web3.TestRPC',),
    ('web3.Tester',),
}


@cast_return_to_tuple
def load_default_config_info(config_defaults=POPULUS_CONFIG_DEFAULTS):
    for config_value in config_defaults:
        if len(config_value) == 1:
            write_path = config_value[0]
            merge_strategy = None
            config_file_name = "{0}.config.json".format(write_path)
            callback = None
        elif len(config_value) == 2:
            write_path, merge_strategy = config_value
            config_file_name = "{0}.config.json".format(write_path)
            callback = None
        elif len(config_value) == 3:
            write_path, merge_strategy, callback = config_value
            config_file_name = "{0}.config.json".format(write_path)
        elif len(config_value) == 4:
            write_path, merge_strategy, callback, config_file_name = config_value
        else:
            raise ValueError("Invalid Default Configuration")

        config_file_path = os.path.join(ASSETS_DIR, config_file_name)
        loaded_config = anyconfig.load(config_file_path)

        if callback is not None:
            processed_config = callback(loaded_config)
        else:
            processed_config = loaded_config

        yield write_path, processed_config, merge_strategy


def apply_default_configs(config, default_configs):
    merged_config = copy.deepcopy(config)

    for write_path, default_config, merge_strategy in default_configs:
        if has_nested_key(merged_config, write_path):
            if not merge_strategy:
                continue
            sub_config = get_nested_key(merged_config, write_path)
            resolved_sub_config = resolve_config(sub_config, config)
            sub_config_with_merge_rules = anyconfig.to_container(
                copy.deepcopy(resolved_sub_config),
                ac_merge=merge_strategy,
            )
            sub_config_with_merge_rules.update(default_config)

            set_nested_key(merged_config, write_path, sub_config_with_merge_rules)
        else:
            set_nested_key(merged_config, write_path, default_config)

    return merged_config
