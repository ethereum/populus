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

from web3 import (
    IPCProvider,
    HTTPProvider,
)


from populus.utils.filesystem import (
    tempdir,
)


from populus.utils.geth import (
    get_geth_logfile_path,
    get_base_blockchain_storage_dir,
)

from .base import (
    BaseChain,
)


class LoggedDevGethProcess(LoggingMixin, DevGethProcess):
    def __init__(self, chain_dir, blockchains_dir, chain_name, overrides):
        stdout_logfile_path = get_geth_logfile_path(
            chain_dir,
            chain_name,
            'stdout'
        )
        stderr_logfile_path = get_geth_logfile_path(
            chain_dir,
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


class LoggedTestnetGethProccess(LoggingMixin, TestnetGethProcess):
    def __init__(self, chain_dir, geth_kwargs):
        super(LoggedTestnetGethProccess, self).__init__(
            geth_kwargs=geth_kwargs,
        )


class LoggedMainnetGethProcess(LoggingMixin, LiveGethProcess):
    def __init__(self, chain_dir, geth_kwargs):
        super(LoggedMainnetGethProcess, self).__init__(
            geth_kwargs=geth_kwargs,
            stdout_logfile_path=get_geth_logfile_path(
                chain_dir,
                'mainnet',
                'stdout'
            ),
            stderr_logfile_path=get_geth_logfile_path(
                chain_dir,
                'mainnet',
                'stderr',
            ),
        )


class BaseGethChain(BaseChain):
    stack = None
    geth = None

    def initialize_chain(self):
        # context manager shenanigans
        self.stack = ExitStack()
        self.geth = self.get_geth_process_instance()

    def get_web3_config(self):
        base_config = super(BaseGethChain, self).get_web3_config()
        config = copy.deepcopy(base_config)
        if not config.get('provider.settings'):
            if issubclass(base_config.provider_class, IPCProvider):
                config['provider.settings.ipc_path'] = self.geth.ipc_path
            elif issubclass(base_config.provider_class, HTTPProvider):
                config['provider.settings.endpoint_uri'] = "http://127.0.0.1:{0}".format(
                    self.geth.rpc_port,
                )
            else:
                raise ValueError("Unknown provider type")
        return config

    @property
    def geth_kwargs(self):
        return self.config.get('chain.settings', {})

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

        self._running = True

        return self

    def __exit__(self, *exc_info):
        self.stack.close()
        self._running = False


class LocalGethChain(BaseGethChain):
    def get_geth_process_instance(self):
        return LoggedDevGethProcess(
            chain_dir=self.chain_dir,
            blockchains_dir=get_base_blockchain_storage_dir(self.chain_dir),
            chain_name=self.chain_name,
            overrides=self.geth_kwargs,
        )


class TemporaryGethChain(BaseGethChain):
    def get_geth_process_instance(self):
        tmp_chain_dir = self.stack.enter_context(tempdir())
        base_blockchain_storage_dir = get_base_blockchain_storage_dir(tmp_chain_dir)

        return LoggedDevGethProcess(
            chain_dir=self.chain_dir,
            blockchains_dir=base_blockchain_storage_dir,
            chain_name=self.chain_name,
            overrides=self.geth_kwargs,
        )


class TestnetChain(BaseGethChain):
    def get_geth_process_instance(self):
        return LoggedTestnetGethProccess(
            chain_dir=self.chain_dir,
            geth_kwargs=self.geth_kwargs,
        )


class MainnetChain(BaseGethChain):
    def get_geth_process_instance(self):
        return LoggedMainnetGethProcess(
            chain_dir=self.chain_dir,
            geth_kwargs=self.geth_kwargs,
        )
