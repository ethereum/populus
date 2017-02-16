import os
import sys
import datetime

from .filesystem import (
    remove_dir_if_exists,
    remove_file_if_exists,
    normpath,
)
from .chains import (
    get_base_blockchain_storage_dir,
)


@normpath
def get_data_dir(project_dir, chain_name):
    base_blockchain_storage_dir = get_base_blockchain_storage_dir(project_dir)
    return os.path.join(base_blockchain_storage_dir, chain_name)


CHAINDATA_DIR = './chaindata'


@normpath
def get_chaindata_dir(data_dir):
    return os.path.join(data_dir, CHAINDATA_DIR)


DAPP_DIR = './dapp'


@normpath
def get_dapp_dir(data_dir):
    return os.path.join(data_dir, DAPP_DIR)


NODEKEY_FILENAME = 'nodekey'


@normpath
def get_nodekey_path(data_dir):
    return os.path.join(data_dir, NODEKEY_FILENAME)


IPC_FILENAME = 'geth.ipc'


@normpath
def get_geth_ipc_path(data_dir):
    return os.path.join(data_dir, IPC_FILENAME)


@normpath
def get_geth_default_datadir_path(testnet=False):
    if testnet:
        testnet = "ropsten"
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


@normpath
def get_geth_default_ipc_path(testnet=False):
    data_dir = get_geth_default_datadir_path(testnet=testnet)

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


@normpath
def get_geth_logfile_path(project_dir, prefix, suffix):
    logs_dir = os.path.join(project_dir, 'logs')
    logfile_name = datetime.datetime.now().strftime(
        'geth-%Y%m%d-%H%M%S-{prefix}-{suffix}.log'.format(
            prefix=prefix, suffix=suffix,
        ),
    )
    return os.path.join(logs_dir, logfile_name)


def reset_chain(data_dir):
    chaindata_dir = get_chaindata_dir(data_dir)
    remove_dir_if_exists(chaindata_dir)

    dapp_dir = get_dapp_dir(data_dir)
    remove_dir_if_exists(dapp_dir)

    nodekey_path = get_nodekey_path(data_dir)
    remove_file_if_exists(nodekey_path)

    geth_ipc_path = get_geth_ipc_path(data_dir)
    remove_file_if_exists(geth_ipc_path)
