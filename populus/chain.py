import contextlib
import functools

import click

from geth import (
    DevGethProcess,
    InterceptedStreamsMixin,
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
    get_geth_logfile_path,
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


class LocalChainGethProcess(InterceptedStreamsMixin, DevGethProcess):
    def __init__(self, *args, **kwargs):
        super(LocalChainGethProcess, self).__init__(*args, **kwargs)
        self.register_stdout_callback(click.echo)
        self.register_stderr_callback(functools.partial(click.echo, err=True))


@contextlib.contextmanager
def dev_geth_process(project_dir, chain_name):
    blockchains_dir = get_blockchains_dir(project_dir)
    with LocalChainGethProcess(chain_name=chain_name, base_dir=blockchains_dir) as geth:
        yield geth


class TestingGethProcess(LoggingMixin, DevGethProcess):
    pass


@contextlib.contextmanager
def testing_geth_process(project_dir, test_name):
    with tempdir() as tmp_project_dir:
        blockchains_dir = get_blockchains_dir(tmp_project_dir)
        geth = TestingGethProcess(
            chain_name='tmp-chain',
            base_dir=blockchains_dir,
            stdout_logfile_path=get_geth_logfile_path(project_dir, test_name, 'stdout'),
            stderr_logfile_path=get_geth_logfile_path(project_dir, test_name, 'stderr'),
        )
        with geth as running_geth:
            if running_geth.is_mining:
                running_geth.wait_for_dag(600)
            if running_geth.ipc_enabled:
                running_geth.wait_for_ipc(30)
            if running_geth.rpc_enabled:
                running_geth.wait_for_rpc(30)
            yield running_geth
