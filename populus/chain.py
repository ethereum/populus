import contextlib

import gevent
import requests

from pygeth import (
    DevGethProcess as _DevGethProcess,
    LoggingMixin,
)
from populus.utils.filesystem import (
    remove_file_if_exists,
    remove_dir_if_exists,
    get_blockchains_dir,
    tempdir,
)
from populus.utils.chain import (
    get_chaindata_dir,
    get_dapp_dir,
    get_nodekey_path,
    get_geth_ipc_path,
)


def reset_chain(data_dir):
    chaindata_dir = get_chaindata_dir(data_dir)
    remove_dir_if_exists(chaindata_dir)

    dapp_dir = get_dapp_dir(data_dir)
    remove_dir_if_exists(dapp_dir)

    nodekey_path = get_nodekey_path(data_dir)
    remove_file_if_exists(nodekey_path)

    geth_ipc_path = get_geth_ipc_path(data_dir)
    remove_file_if_exists(geth_ipc_path)


class DevGethProcess(LoggingMixin, _DevGethProcess):
    pass


@contextlib.contextmanager
def dev_geth_process(project_dir, chain_name):
    blockchains_dir = get_blockchains_dir(project_dir)
    with DevGethProcess(chain_name=chain_name, base_dir=blockchains_dir) as geth:
        yield geth


@contextlib.contextmanager
def testing_geth_process():
    with tempdir() as project_dir:
        with dev_geth_process(project_dir, 'tmp-chain') as geth:
            if geth.is_mining:
                geth.wait_for_dag(600)
            if geth.ipc_enabled:
                geth.wait_for_ipc(30)
            if geth.rpc_enabled:
                geth.wait_for_rpc(30)
            yield geth
