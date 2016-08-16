import functools
import contextlib

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

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
from populus.utils.functional import (
    cached_property,
)
from populus.utils.networking import (
    get_open_port,
    wait_for_http_connection,
)
from populus.utils.module_loading import (
    import_string,
)
from populus.utils.transactions import (
    get_contract_address_from_txn,
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

from populus.migrations.registrar import (
    get_compiled_registrar_contract,
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


class Chain(object):
    """
    Base class for how populus interacts with the blockchain.
    """
    project = None

    def __init__(self, project, chain_name):
        self.project = project
        self.chain_name = chain_name

    @property
    def web3(self):
        raise NotImplementedError("Must be implemented by subclasses")

    @property
    def chain_config(self):
        raise NotImplementedError("Must be implemented by subclasses")

    @cached_property
    def contract_factories(self):
        return package_contracts(self.web3, self.project.compiled_contracts)

    @property
    def RegistrarFactory(self):
        return get_compiled_registrar_contract(self.web3)

    @property
    def registrar(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __enter__(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestRPCChain(Chain):
    provider = None
    port = None

    @cached_property
    def web3(self):
        if self.provider is None or not self._running:
            raise ValueError(
                "TesterChain instances must be running to access the web3 "
                "object."
            )
        return Web3(self.provider)

    @cached_property
    def chain_config(self):
        config = self.project.config.chains[self.chain_name]
        config.update({
            'registrar': self.registrar.address,
        })
        return config

    @cached_property
    def registrar(self):
        RegistrarFactory = get_compiled_registrar_contract(self.web3)
        deploy_txn_hash = RegistrarFactory.deploy()
        registrar_address = get_contract_address_from_txn(
            self.web3,
            deploy_txn_hash,
            1,
        )
        registrar = RegistrarFactory(address=registrar_address)
        return registrar

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
    'rpc_enabled',
    'rpc_addr',
    'rpc_port',
    'rpc_api',
    'prefix_cmd',
    'suffix_args',
    'suffix_kwargs',
}


class BaseGethChain(Chain):
    geth = None
    provider_class = None

    def __init__(self, project, chain_name, provider=IPCProvider, **geth_kwargs):
        super(BaseGethChain, self).__init__(project, chain_name)

        if geth_kwargs is None:
            geth_kwargs = {}

        if is_string(provider):
            provider = import_string(provider)

        # context manager shenanigans
        self.stack = ExitStack()

        self.provider_class = provider
        self.extra_kwargs = {
            key: value
            for key, value in geth_kwargs.items() if key not in GETH_KWARGS
        }
        self.geth_kwargs = {
            key: value
            for key, value in geth_kwargs.items() if key in GETH_KWARGS
        }
        self.geth = self.get_geth_process_instance()

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

            # TODO: web3 should be configured with things like the
            # `defaultAccount` from the project configuration.
        return self._web3

    @property
    def chain_config(self):
        return self.project.config.chains[self.chain_name]

    @cached_property
    def registrar(self):
        return get_compiled_registrar_contract(
            self.web3,
            address=self.chain_config['registrar'],
        )

    def get_geth_process_instance(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __enter__(self, *args, **kwargs):
        self.stack.enter_context(self.geth)

        if self.geth.is_mining:
            self.geth.wait_for_dag(600)
        if self.geth.ipc_enabled:
            self.geth.wait_for_ipc(30)
        if self.geth.rpc_enabled:
            self.geth.wait_for_rpc(30)

        return self

    def __exit__(self, *exc_info):
        self.stack.close()


class LocalGethChain(BaseGethChain):
    def get_geth_process_instance(self):
        return LoggedDevGethProcess(
            project_dir=self.project.project_dir,
            blockchains_dir=self.project.blockchains_dir,
            chain_name=self.chain_name,
            overrides=self.geth_kwargs,
        )


class TemporaryGethChain(BaseGethChain):
    def get_geth_process_instance(self):
        tmp_project_dir = self.stack.enter_context(tempdir())
        blockchains_dir = get_blockchains_dir(tmp_project_dir)

        return LoggedDevGethProcess(
            project_dir=self.project.project_dir,
            blockchains_dir=blockchains_dir,
            chain_name=self.chain_name,
            overrides=self.geth_kwargs,
        )

    @cached_property
    def registrar(self):
        if 'registrar' in self.chain_config:
            registrar_address = self.chain_config['registrar']
        else:
            # TODO: this lazy creation might cause some problems.
            RegistrarFactory = get_compiled_registrar_contract(self.web3)
            deploy_txn_hash = RegistrarFactory.deploy()
            registrar_address = get_contract_address_from_txn(
                self.web3,
                deploy_txn_hash,
                60,
            )
        registrar = RegistrarFactory(address=registrar_address)
        return registrar


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
