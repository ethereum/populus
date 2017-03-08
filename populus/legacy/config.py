import os
import shutil

from populus.config import (
    load_default_config,
    write_config,
)
from populus.config.versions import (
    V1,
)

from populus.utils.six import configparser
from populus.utils.mappings import (
    set_nested_key,
    deep_merge_dicts,
)
from populus.utils.config import (
    get_json_config_file_path,
    check_if_json_config_file_exists,
)


INI_CONFIG_FILENAME = './populus.ini'


def get_ini_config_file_path(project_dir=None):
    if project_dir is None:
        project_dir = os.getcwd()

    ini_config_file_path = os.path.join(project_dir, INI_CONFIG_FILENAME)
    return ini_config_file_path


def check_if_ini_config_file_exists(project_dir=None):
    if project_dir is None:
        project_dir = os.getcwd()

    ini_config_file_path = get_ini_config_file_path(project_dir)
    return os.path.exists(ini_config_file_path)


PROVIDER_LOOKUP = {
    'mainnet': 'populus.chain.MainnetChain',
    'testnet': 'populus.chain.TestnetChain',
    'morden': 'populus.chain.TestnetChain',
    'ropsten': 'populus.chain.TestnetChain',
    'testrpc': 'populus.chain.TestRPCChain',
    'tester': 'populus.chain.TesterChain',
    'temp': 'populus.chain.TemporaryGethChain',
}


def translate_legacy_ini_config_file(ini_config_file_path):
    config = configparser.ConfigParser()
    config.read(ini_config_file_path)

    upgraded_config = {}

    for section in config.sections():
        if section == 'populus':
            for key, value in config.items('populus'):
                if key == 'contracts_dir':
                    set_nested_key(upgraded_config, 'compilation.contracts_dir', value)
                else:
                    set_nested_key(upgraded_config, 'populus.{0}'.format(key), value)
            continue
        elif section.startswith('chain:'):
            _, _, chain_name = section.partition(':')
            key_prefix = "chains.{0}".format(chain_name)

            if not config.options(section):
                set_nested_key(
                    upgraded_config,
                    '.'.join((key_prefix, 'chain.class')),
                    PROVIDER_LOOKUP.get(chain_name, 'populus.chain.LocalGethChain'),
                )
                set_nested_key(
                    upgraded_config,
                    '.'.join((key_prefix, 'web3.provider.class')),
                    'web3.providers.ipc.IPCProvider',
                )
                continue

            if config.has_option(section, 'is_external') and config.get(section, 'is_external'):
                set_nested_key(
                    upgraded_config,
                    '.'.join((key_prefix, 'chain.class')),
                    'populus.chain.ExternalChain',
                )
            else:
                set_nested_key(
                    upgraded_config,
                    '.'.join((key_prefix, 'chain.class')),
                    PROVIDER_LOOKUP.get(chain_name, 'populus.chain.LocalGethChain'),
                )

            if config.has_option(section, 'provider'):
                provider_class_path = config.get(section, 'provider')
                if provider_class_path == 'web3.providers.rpc.RPCProvider':
                    if config.has_option(section, 'rpc_host'):
                        rpc_host = config.get(section, 'rpc_host')
                    else:
                        rpc_host = 'localhost'
                    if config.has_option(section, 'rpc_port'):
                        rpc_port = config.get(section, 'rpc_port')
                    else:
                        rpc_port = '8545'
                    set_nested_key(
                        upgraded_config,
                        '.'.join((key_prefix, 'web3.provider.class')),
                        'web3.providers.rpc.HTTPProvider',
                    )
                    set_nested_key(
                        upgraded_config,
                        '.'.join((key_prefix, 'web3.provider.settings.endpoint_uri')),
                        'http://{0}:{1}'.format(rpc_host, rpc_port),
                    )
                else:
                    set_nested_key(
                        upgraded_config,
                        '.'.join((key_prefix, 'web3.provider.class')),
                        config.get(section, 'provider'),
                    )
            else:
                set_nested_key(
                    upgraded_config,
                    '.'.join((key_prefix, 'web3.provider.class')),
                    'web3.providers.ipc.IPCProvider',
                )

            if config.has_option(section, 'ipc_path'):
                set_nested_key(
                    upgraded_config,
                    '.'.join((key_prefix, 'web3.provider.settings.ipc_path')),
                    config.get(section, 'ipc_path'),
                )

            if config.has_option(section, 'default_account'):
                set_nested_key(
                    upgraded_config,
                    '.'.join((key_prefix, 'web3.eth.default_account')),
                    config.get(section, 'default_account'),
                )
            elif config.has_option(section, 'deploy_from'):
                set_nested_key(
                    upgraded_config,
                    '.'.join((key_prefix, 'web3.eth.default_account')),
                    config.get(section, 'deploy_from'),
                )

    return upgraded_config


def upgrade_legacy_config_file(project_dir):
    has_ini_config = check_if_ini_config_file_exists(project_dir)
    has_json_config = check_if_json_config_file_exists(project_dir)

    if not has_ini_config:
        raise ValueError("No `populus.ini` file found")
    elif has_json_config:
        raise ValueError(
            "Cannot upgrade config file if there is already an existing "
            "`populus.json` file."
        )

    ini_config_file_path = get_ini_config_file_path(project_dir)
    json_config_file_path = get_json_config_file_path(project_dir)

    upgraded_config = translate_legacy_ini_config_file(ini_config_file_path)

    default_config = load_default_config(version=V1)
    config = deep_merge_dicts(default_config, upgraded_config)

    write_config(
        project_dir,
        config,
        json_config_file_path,
    )
    backup_ini_config_file_path = "{0}.bak".format(ini_config_file_path)
    shutil.move(ini_config_file_path, backup_ini_config_file_path)
    return backup_ini_config_file_path
