import os
import sys
import datetime

from web3 import (
    Web3,
    RPCProvider,
    IPCProvider,
    HTTPProvider,
    TestRPCProvider,
)

from .module_loading import (
    import_string,
)
from .filesystem import (
    get_blockchains_dir,
)


def get_data_dir(project_dir, chain_name):
    blockchains_dir = get_blockchains_dir(project_dir)
    return os.path.join(blockchains_dir, chain_name)


CHAINDATA_DIR = './chaindata'


def get_chaindata_dir(data_dir):
    return os.path.join(data_dir, CHAINDATA_DIR)


DAPP_DIR = './dapp'


def get_dapp_dir(data_dir):
    return os.path.join(data_dir, DAPP_DIR)


NODEKEY_FILENAME = 'nodekey'


def get_nodekey_path(data_dir):
    return os.path.join(data_dir, NODEKEY_FILENAME)


IPC_FILENAME = 'geth.ipc'


def get_geth_ipc_path(data_dir):
    return os.path.join(data_dir, IPC_FILENAME)


def get_default_datadir_path(testnet=False):
    if testnet:
        testnet = "testnet"
    else:
        testnet = ""

    if sys.platform == 'darwin':
        return os.path.expanduser(os.path.join(
            "~",
            "Library",
            "Ethereum",
            testnet,
        ))
    elif sys.platform.startswith('linux'):
        return os.path.expanduser(os.path.join(
            "~",
            ".ethereum",
            testnet,
        ))
    elif sys.platform == 'win32':
        return os.path.expanduser(os.path.join(
            "~",
            "AppData",
            "Roaming",
            "Ethereum",
        ))
    else:
        raise ValueError(
            "Unsupported platform '{0}'.  Only darwin/linux2/win32 are "
            "supported.".format(sys.platform)
        )


def get_default_ipc_path(testnet=False):
    data_dir = get_default_datadir_path(testnet=testnet)

    if sys.platform == 'darwin' or sys.platform.startswith('linux'):
        return os.path.join(data_dir, "geth.ipc")
    elif sys.platform == 'win32':
        return os.path.expanduser(os.path.join(
            "~",
            "AppData",
            "Roaming",
            "Ethereum",
        ))
    else:
        raise ValueError(
            "Unsupported platform '{0}'.  Only darwin/linux2/win32 are "
            "supported.".format(sys.platform)
        )


def get_geth_logfile_path(project_dir, prefix, suffix):
    logs_dir = os.path.join(project_dir, 'logs')
    logfile_name = datetime.datetime.now().strftime(
        'geth-%Y%m%d-%H%M%S-{prefix}-{suffix}.log'.format(
            prefix=prefix, suffix=suffix,
        ),
    )
    return os.path.join(logs_dir, logfile_name)


def setup_web3_from_config(web3_config):
    ProviderClass = import_string(web3_config['provider.class'])

    provider_kwargs = {}

    if issubclass(ProviderClass, (RPCProvider, TestRPCProvider)):
        if 'provider.settings.rpc_host' in web3_config:
            provider_kwargs['host'] = web3_config['provider.settings.rpc_host']

        if 'provider.settings.rpc_port' in web3_config:
            provider_kwargs['port'] = web3_config['provider.settings.rpc_port']

        if 'provider.settings.use_ssl' in web3_config:
            provider_kwargs['ssl'] = web3_config['provider.settings.use_ssl']
    elif issubclass(ProviderClass, IPCProvider):
        if 'provider.settings.ipc_path' in web3_config:
            provider_kwargs['ipc_path'] = web3_config['provider.settings.ipc_path']
    elif issubclass(ProviderClass, HTTPProvider):
        if 'provider.settings.rpc_endpoint' in web3_config:
            provider_kwargs['endpoint_uri'] = web3_config['provider.settings.endpoint_uri']

    web3 = Web3(ProviderClass(**provider_kwargs))

    if 'eth.default_account' in web3_config:
        web3.eth.defaultAccount = web3_config['eth.default_account']

    return web3
