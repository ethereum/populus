import contextlib
import functools

import click

from testrpc import testrpc

from web3.utils.types import is_string

from web3.providers.rpc import TestRPCProvider
from web3 import (
    Web3,
    RPCProvider,
    IPCProvider,
)

from geth import (
    DevGethProcess,
    LiveGethProcess,
    TestnetGethProcess,
    InterceptedStreamsMixin,
    LoggingMixin,
)
from populus.utils.networking import (
    get_open_port,
    wait_for_http_connection,
)
from populus.utils.module_loading import (
    import_string,
)
from populus.utils.filesystem import (
    remove_file_if_exists,
    remove_dir_if_exists,
    get_blockchains_dir,
    tempdir,
)
from populus.utils.contracts import (
    package_contracts,
)
from populus.utils.chains import (
    get_chaindata_dir,
    get_dapp_dir,
    get_nodekey_path,
    get_geth_ipc_path,
    get_geth_logfile_path,
)


TESTNET_BLOCK_1_HASH = '0xad47413137a753b2061ad9b484bf7b0fc061f654b951b562218e9f66505be6ce'  # noqa
MAINNET_BLOCK_1_HASH = '0x88e96d4537bea4d9c05d12549907b32561d3bf31f45aae734cdc119f13406cb6'  # noqa


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
    local_chain_geth = LocalChainGethProcess(
        chain_name=chain_name,
        base_dir=blockchains_dir,
    )
    with local_chain_geth as geth:
        yield geth


class LoggedDevGethProcess(LoggingMixin, DevGethProcess):
    def __init__(self, project_dir, blockchains_dir, chain_name, overrides):
        super(LoggedDevGethProcess, self).__init__(
            overrides=overrides,
            chain_name=chain_name,
            base_dir=blockchains_dir,
            stdout_logfile_path=get_geth_logfile_path(
                project_dir,
                chain_name,
                'stdout'
            ),
            stderr_logfile_path=get_geth_logfile_path(
                project_dir,
                chain_name,
                'stderr',
            ),

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


class Chain(object):
    """
    Base class for how populus interacts with the blockchain.
    """
    project = None

    def __init__(self, project):
        self.project = project

    @property
    def web3(self):
        raise NotImplementedError("Must be implemented by subclasses")

    @property
    def contract_factories(self):
        return package_contracts(self.web3, self.project.compiled_contracts)

    def __enter__(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestRPCChain(Chain):
    provider = None
    port = None
    _web3 = None

    @property
    def web3(self):
        if self._web3 is None:
            if self.provider is None:
                raise ValueError(
                    "TesterChain instances must be running to access the web3 "
                    "object."
                )
            self._web3 = Web3(self.provider)
        return self._web3

    _running = False

    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        if self.port is None:
            self.port = get_open_port()

        self.provider = TestRPCProvider(port=self.port)

        testrpc.full_reset()
        testrpc.rpc_configure('eth_mining', False)
        testrpc.rpc_configure('eth_protocolVersion', '0x3f')
        testrpc.rpc_configure('net_version', 1)
        testrpc.evm_mine()

        wait_for_http_connection('127.0.0.1', self.port)
        self._running = True
        return self

    def __exit__(self, *exc_info):
        if not self._running:
            raise ValueError("The TesterChain is not running")
        try:
            self.provider.server.shutdown()
            self.provider.server.server_close()
        finally:
            self._running = False


class BaseGethChain(Chain):
    geth = None
    provider_class = None

    def __init__(self, project, provider=IPCProvider, **geth_kwargs):
        if geth_kwargs is None:
            geth_kwargs = {}

        if is_string(provider):
            provider = import_string(provider)

        self.provider_class = provider
        self.geth_kwargs = geth_kwargs

        super(BaseGethChain, self).__init__(project)

    _web3 = None

    @property
    def web3(self):
        if not self.geth.is_running:
            raise ValueError(
                "Underlying geth process doesn't appear to be running"
            )
        if self._web3 is None:
            if issubclass(self.provider_class, IPCProvider):
                provider = IPCProvider(self.geth.ipc_path)
            elif issubclass(self.provider, RPCProvider):
                provider = RPCProvider(port=self.geth.rpc_port)
            else:
                raise NotImplementedError(
                    "Unsupported provider class {0!r}.  Must be one of "
                    "IPCProvider or RPCProvider"
                )
            self._web3 = Web3(provider)
        return self._web3

    def get_geth_process_instance(self, *args, **kwargs):
        raise NotImplementedError("Must be implemented by subclasses")

    def __enter__(self, *args, **kwargs):
        # context manager shenanigans
        self.stack = contextlib.ExitStack()

        self.geth = self.stack.enter_context(
            self.get_geth_process_instance(
                *args,
                **kwargs
            )
        )

        if self.geth.is_mining:
            self.geth.wait_for_dag(600)
        if self.geth.ipc_enabled:
            self.geth.wait_for_ipc(30)
        if self.geth.rpc_enabled:
            self.geth.wait_for_rpc(30)

        return self

    def __exit__(self, *exc_info):
        self.stack.close()
        del self.stack


class LocalGethChain(BaseGethChain):
    def __init__(self, *args, **kwargs):
        self.chain_name = kwargs.pop('chain_name')
        super(LocalGethChain, self).__init__(*args, **kwargs)

    def get_geth_process_instance(self, *args, **kwargs):
        return LoggedDevGethProcess(
            *args,
            project_dir=self.project.project_dir,
            blockchains_dir=self.project.blockchains_dir,
            chain_name=self.chain_name,
            overrides=self.geth_kwargs,
            **kwargs
        )


class TemporaryGethChain(BaseGethChain):
    def get_geth_process_instance(self,
                                  name='temporary-geth-chain',
                                  *args,
                                  **kwargs):
        tmp_project_dir = self.stack.enter_context(tempdir())
        blockchains_dir = get_blockchains_dir(tmp_project_dir)

        return LoggedDevGethProcess(
            *args,
            project_dir=self.project.project_dir,
            blockchains_dir=blockchains_dir,
            chain_name=name,
            overrides=self.geth_kwargs,
            **kwargs
        )


class MordenChain(BaseGethChain):
    def get_geth_process_instance(self, *args, **kwargs):
        return LoggedMordenGethProccess(
            *args,
            project_dir=self.project.project_dir,
            geth_kwargs=self.geth_kwargs,
            **kwargs
        )


class MainnetChain(BaseGethChain):
    def get_geth_process_instance(self, *args, **kwargs):
        return LoggedMainnetGethProcess(
            *args,
            project_dir=self.project.project_dir,
            geth_kwargs=self.geth_kwargs,
            **kwargs
        )
