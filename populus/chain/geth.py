from __future__ import absolute_import

import copy

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

from geth import (
    DevGethProcess,
    LiveGethProcess,
    TestnetGethProcess,
    LoggingMixin,
)

from populus.utils.chains import (
    get_base_blockchain_storage_dir,
)
from populus.utils.geth import (
    get_geth_logfile_path,
)
from populus.utils.filesystem import (
    tempdir,
)

from .base import (
    Chain,
)


GETH_KWARGS = {
    'data_dir',
    'geth_executable',
    'max_peers',
    'network_id',
    'no_discover',
    'mine',
    'autodag',
    'miner_threads',
    'nice',
    'unlock',
    'password',
    'port',
    'verbosity',
    'ipc_disable',
    'ipc_path',
    'ipc_api',
    'ws_enabled',
    'ws_enabled',
    'ws_addr',
    'ws_origins',
    'ws_port',
    'ws_api',
    'rpc_enabled',
    'rpc_addr',
    'rpc_port',
    'rpc_api',
    'prefix_cmd',
    'suffix_args',
    'suffix_kwargs',
}


class LoggedDevGethProcess(LoggingMixin, DevGethProcess):
    def __init__(self, project_dir, blockchains_dir, chain_name, overrides):
        stdout_logfile_path = get_geth_logfile_path(
            project_dir,
            chain_name,
            'stdout'
        )
        stderr_logfile_path = get_geth_logfile_path(
            project_dir,
            chain_name,
            'stderr',
        )
        super(LoggedDevGethProcess, self).__init__(
            overrides=overrides,
            chain_name=chain_name,
            base_dir=blockchains_dir,
            stdout_logfile_path=stdout_logfile_path,
            stderr_logfile_path=stderr_logfile_path,
        )


class LoggedMordenGethProccess(LoggingMixin, TestnetGethProcess):
    def __init__(self, project_dir, geth_kwargs):
        super(LoggedMordenGethProccess, self).__init__(
            geth_kwargs=geth_kwargs,
        )


class LoggedMainnetGethProcess(LoggingMixin, LiveGethProcess):
    def __init__(self, project_dir, geth_kwargs):
        super(LoggedMainnetGethProcess, self).__init__(
            geth_kwargs=geth_kwargs,
            stdout_logfile_path=get_geth_logfile_path(
                project_dir,
                'mainnet',
                'stdout'
            ),
            stderr_logfile_path=get_geth_logfile_path(
                project_dir,
                'mainnet',
                'stderr',
            ),
        )


class BaseGethChain(Chain):
    geth = None
    provider_class = None

    def __init__(self, project, chain_name, **geth_kwargs):
        super(BaseGethChain, self).__init__(project, chain_name)

        if geth_kwargs is None:
            geth_kwargs = {}

        # context manager shenanigans
        self.stack = ExitStack()

        self.extra_kwargs = {
            key: value
            for key, value in geth_kwargs.items() if key not in GETH_KWARGS
        }
        self.geth_kwargs = {
            key: value
            for key, value in geth_kwargs.items() if key in GETH_KWARGS
        }
        self.geth = self.get_geth_process_instance()

    def get_web3_config(self):
        web3_config = copy.deepcopy(super(BaseGethChain, self).get_web3_config())
        web3_config['provider.settings.ipc_path'] = self.geth.ipc_path
        web3_config['provider.settings.rpc_port'] = self.geth.rpc_port
        return web3_config

    def get_geth_process_instance(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __enter__(self, *args, **kwargs):
        self.stack.enter_context(self.geth)

        if self.geth.is_mining:
            self.geth.wait_for_dag(600)
        if self.geth.ipc_enabled:
            self.geth.wait_for_ipc(60)
        if self.geth.rpc_enabled:
            self.geth.wait_for_rpc(60)

        return self

    def __exit__(self, *exc_info):
        self.stack.close()


class LocalGethChain(BaseGethChain):
    def get_geth_process_instance(self):
        return LoggedDevGethProcess(
            project_dir=self.project.project_dir,
            blockchains_dir=self.project.base_blochchain_storage_dir,
            chain_name=self.chain_name,
            overrides=self.geth_kwargs,
        )


class TemporaryGethChain(BaseGethChain):
    def get_geth_process_instance(self):
        tmp_project_dir = self.stack.enter_context(tempdir())
        base_blochcain_storage_dir = get_base_blockchain_storage_dir(tmp_project_dir)

        return LoggedDevGethProcess(
            project_dir=self.project.project_dir,
            blockchains_dir=base_blochcain_storage_dir,
            chain_name=self.chain_name,
            overrides=self.geth_kwargs,
        )


class MordenChain(BaseGethChain):
    def get_geth_process_instance(self):
        return LoggedMordenGethProccess(
            project_dir=self.project.project_dir,
            geth_kwargs=self.geth_kwargs,
        )


class MainnetChain(BaseGethChain):
    def get_geth_process_instance(self):
        return LoggedMainnetGethProcess(
            project_dir=self.project.project_dir,
            geth_kwargs=self.geth_kwargs,
        )
