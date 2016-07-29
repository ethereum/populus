import os
import datetime

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


def get_geth_logfile_path(project_dir, prefix, suffix):
    logs_dir = os.path.join(project_dir, 'logs')
    logfile_name = datetime.datetime.now().strftime(
        'geth-%Y%m%d-%H%M%S-{prefix}-{suffix}.log'.format(
            prefix=prefix, suffix=suffix,
        ),
    )
    return os.path.join(logs_dir, logfile_name)
