import itertools

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

from pylru import lrucache

from web3.utils.types import is_string

from web3 import (
    Web3,
    RPCProvider,
    IPCProvider,
    TestRPCProvider,
    EthereumTesterProvider,
)

from geth import (
    DevGethProcess,
    LiveGethProcess,
    TestnetGethProcess,
    LoggingMixin,
)
from populus.utils.functional import (
    cached_property,
)
from populus.utils.networking import (
    get_open_port,
    wait_for_connection,
)
from populus.utils.module_loading import (
    import_string,
)
from populus.utils.wait import (
    Wait,
)
from populus.utils.filesystem import (
    remove_file_if_exists,
    remove_dir_if_exists,
    get_blockchains_dir,
    tempdir,
)
from populus.utils.contracts import (
    construct_contract_factories,
    package_contracts,
    get_contract_library_dependencies,
    link_bytecode,
)
from populus.utils.chains import (
    get_chaindata_dir,
    get_dapp_dir,
    get_nodekey_path,
    get_geth_ipc_path,
    get_geth_logfile_path,
)

from populus.migrations.migration import (
    get_compiled_contracts_from_migrations,
)
from populus.migrations.registrar import (
    get_registrar,
)


TESTNET_BLOCK_1_HASH = '0xad47413137a753b2061ad9b484bf7b0fc061f654b951b562218e9f66505be6ce'
MAINNET_BLOCK_1_HASH = '0x88e96d4537bea4d9c05d12549907b32561d3bf31f45aae734cdc119f13406cb6'


def reset_chain(data_dir):
    chaindata_dir = get_chaindata_dir(data_dir)
    remove_dir_if_exists(chaindata_dir)

    dapp_dir = get_dapp_dir(data_dir)
    remove_dir_if_exists(dapp_dir)

    nodekey_path = get_nodekey_path(data_dir)
    remove_file_if_exists(nodekey_path)

    geth_ipc_path = get_geth_ipc_path(data_dir)
    remove_file_if_exists(geth_ipc_path)


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


class ContractError(Exception):
    """
    Base Exception class for errors raised by the Chain contract API.
    """
    pass


class BytecodeMismatchError(ContractError):
    """
    Indicates there is a bytecode mismatch.
    """
    pass


class NoKnownAddress(ContractError):
    """
    Raised when the address for a requested contract is not known.
    """
    pass


class UnknownContract(ContractError):
    """
    Raised when the requested contract name is not found in the compiled
    contracts.
    """
    pass


class Chain(object):
    """
    Base class for how populus interacts with the blockchain.

    :param project: Instance of :class:`populus.project.Project`
    """
    project = None
    chain_name = None
    _factory_cache = None

    def __init__(self, project, chain_name):
        self.project = project
        self.chain_name = chain_name
        self._factory_cache = lrucache(128)

    #
    # Required Public API
    #
    @property
    def web3(self):
        raise NotImplementedError("Must be implemented by subclasses")

    @property
    def wait(self):
        return Wait(self.web3)

    @property
    def chain_config(self):
        raise NotImplementedError("Must be implemented by subclasses")

    @cached_property
    def contract_factories(self):
        if self.project.migrations:
            compiled_contracts = get_compiled_contracts_from_migrations(
                self.project.migrations,
                self,
            )
        else:
            compiled_contracts = self.project.compiled_contracts

        return construct_contract_factories(
            self.web3,
            compiled_contracts,
        )

    @property
    def RegistrarFactory(self):
        return get_registrar(self.web3)

    @property
    def has_registrar(self):
        raise NotImplementedError("Must be implemented by subclasses")

    @property
    def registrar(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __enter__(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    #
    # Utility
    #
    def _extract_library_dependencies(self, bytecode, link_dependencies=None):
        if link_dependencies is None:
            link_dependencies = {}

        all_known_contract_names = set(link_dependencies.keys()).union(
            self.contract_factories.keys(),
        )

        library_dependencies = get_contract_library_dependencies(
            bytecode,
            all_known_contract_names,
        )
        return library_dependencies

    def _link_code(self, bytecodes,
                   link_dependencies=None,
                   validate_bytecode=True,
                   raise_on_error=False):
        if link_dependencies is None:
            link_dependencies = {}

        library_dependencies = set(itertools.chain.from_iterable(
            self._extract_library_dependencies(bytecode, link_dependencies)
            for bytecode in bytecodes
        ))

        # Determine which dependencies would need to be present in the
        # registrar since they were not explicitely declared via the
        # `link_dependencies`.
        registrar_dependencies = set(library_dependencies).difference(
            link_dependencies.keys()
        )
        if registrar_dependencies and not self.has_registrar:
            raise NoKnownAddress(
                "Unable to link bytecode.  Addresses for the following link "
                "dependencies were not provided and this chain does not have a "
                "registrar.\n\n{0}".format(
                    ', '.join(registrar_dependencies),
                )
            )

        # Loop over all of the dependencies and ensure that they are available,
        # raising an exception if they are not.
        for library_name in registrar_dependencies:
            self.is_contract_available(
                library_name,
                link_dependencies=link_dependencies,
                validate_bytecode=validate_bytecode,
                raise_on_error=True,
            )

        registrar_link_dependencies = {
            library_name: self.get_contract(
                library_name,
                link_dependencies=link_dependencies,
                validate_bytecode=validate_bytecode,
            ).address for library_name in registrar_dependencies
        }

        all_link_dependencies = {
            library_name: library_address
            for library_name, library_address
            in itertools.chain(
                link_dependencies.items(),
                registrar_link_dependencies.items(),
            )
        }

        linked_bytecodes = [
            link_bytecode(bytecode, **all_link_dependencies)
            for bytecode in bytecodes
        ]
        return linked_bytecodes

    #
    # Contract API
    #
    def is_contract_available(self,
                              contract_name,
                              link_dependencies=None,
                              validate_bytecode=True,
                              raise_on_error=False):
        if not self.has_registrar:
            raise NoKnownAddress(
                'The `is_contract_available` API is only usable on chains that '
                'have a registrar contract'
            )
        contract_key = 'contract/{name}'.format(name=contract_name)

        if not self.registrar.call().exists(contract_key):
            if raise_on_error:
                raise NoKnownAddress(
                    "Address for contract '{name}' not found in registrar".format(
                        name=contract_name,
                    )
                )
            return False

        if not validate_bytecode:
            return True

        try:
            contract_factory = self.get_contract_factory(
                contract_name,
                link_dependencies=link_dependencies,
            )
        except (NoKnownAddress, BytecodeMismatchError):
            if raise_on_error:
                raise
            return False

        contract_address = self.registrar.call().getAddress(contract_key)

        chain_bytecode = self.web3.eth.getCode(contract_address)

        is_bytecode_match = chain_bytecode == contract_factory.code_runtime
        if not is_bytecode_match and raise_on_error:
            raise BytecodeMismatchError(
                "Bytecode @ {0} does not match expected contract bytecode.\n\n"
                "expected : '{1}'\n"
                "actual   : '{2}'\n".format(
                    contract_address,
                    contract_factory.code_runtime,
                    chain_bytecode,
                ),
            )
        return is_bytecode_match

    def get_contract(self,
                     contract_name,
                     link_dependencies=None,
                     validate_bytecode=True):
        if contract_name not in self.contract_factories:
            raise UnknownContract(
                "No contract found with the name '{0}'.\n\n"
                "Available contracts are: {1}".format(
                    contract_name,
                    ', '.join((name for name in self.contract_factories.keys())),
                )
            )
        self.is_contract_available(
            contract_name,
            link_dependencies=link_dependencies,
            validate_bytecode=validate_bytecode,
            raise_on_error=True,
        )

        contract_factory = self.get_contract_factory(
            contract_name,
            link_dependencies=link_dependencies,
        )
        contract_key = 'contract/{name}'.format(name=contract_name)
        contract_address = self.registrar.call().getAddress(contract_key)
        contract = contract_factory(address=contract_address)
        return contract

    def get_contract_factory(self,
                             contract_name,
                             link_dependencies=None):
        cache_key = (contract_name,) + tuple(sorted((link_dependencies or {}).items()))
        if cache_key in self._factory_cache:
            return self._factory_cache[cache_key]
        if contract_name not in self.contract_factories:
            raise UnknownContract(
                "No contract found with the name '{0}'.\n\n"
                "Available contracts are: {1}".format(
                    contract_name,
                    ', '.join((name for name in self.contract_factories.keys())),
                )
            )

        base_contract_factory = self.contract_factories[contract_name]

        if link_dependencies is not False:
            code, code_runtime = self._link_code(
                bytecodes=[
                    base_contract_factory.code,
                    base_contract_factory.code_runtime,
                ],
                link_dependencies=link_dependencies,
            )
        else:
            code, code_runtime = (
                base_contract_factory.code,
                base_contract_factory.code_runtime,
            )

        contract_factory = self.web3.eth.contract(
            code=code,
            code_runtime=code_runtime,
            abi=base_contract_factory.abi,
            source=base_contract_factory.source,
        )
        self._factory_cache[cache_key] = contract_factory
        return contract_factory

    @property
    def deployed_contracts(self):
        contract_classes = {
            contract_name: self.get_contract(contract_name)
            for contract_name in self.contract_factories.keys()
            if self.is_contract_available(contract_name)
        }
        return package_contracts(contract_classes)


class ExternalChain(Chain):
    """
    Chain class to represent an externally running blockchain that is not
    locally managed.  This class only houses a pre-configured web3 instance.
    """
    def __init__(self, project, chain_name, *args, **kwargs):
        super(ExternalChain, self).__init__(project, chain_name)

        provider_import_path = kwargs.pop(
            'provider',
            'web3.providers.ipc.IPCProvider',
        )
        provider_class = import_string(provider_import_path)

        if provider_class == RPCProvider:
            host = kwargs.pop('host', '127.0.0.1')
            # TODO: this integer casting needs to be done downstream in
            # web3.py.
            port = int(kwargs.pop('port', 8545))
            provider = provider_class(host=host, port=port)
        elif provider_class == IPCProvider:
            ipc_path = kwargs.pop('ipc_path', None)
            provider = provider_class(ipc_path=ipc_path)
        else:
            raise NotImplementedError(
                "Only the IPCProvider and RPCProvider provider classes are "
                "currently supported for external chains."
            )

        self._web3 = Web3(provider)

    @property
    def chain_config(self):
        return self.project.config.chains[self.chain_name]

    @property
    def web3(self):
        if 'default_account' in self.chain_config:
            self._web3.eth.defaultAccount = self.chain_config['default_account']
        return self._web3

    def __enter__(self):
        return self

    @property
    def has_registrar(self):
        return 'registrar' in self.chain_config

    @cached_property
    def registrar(self):
        if not self.has_registrar:
            raise KeyError(
                "The configuration for the {0} chain does not include a "
                "registrar.  Please set this value to the address of the "
                "deployed registrar contract.".format(self.chain_name)
            )
        return get_registrar(
            self.web3,
            address=self.chain_config['registrar'],
        )


def testrpc_fn_proxy(fn_name):
    def inner(self, *args, **kwargs):
        fn = getattr(self.rpc_methods, fn_name)
        return fn(*args, **kwargs)
    inner.__name__ = fn_name
    return inner


class BaseTesterChain(Chain):
    provider = None
    port = None

    @cached_property
    def web3(self):
        if self.provider is None or not self._running:
            raise ValueError(
                "TesterChain instances must be running to access the web3 "
                "object."
            )
        _web3 = Web3(self.provider)

        if 'default_account' in self.chain_config:
            _web3.eth.defaultAccount = self.chain_config['default_account']

        return _web3

    @property
    def chain_config(self):
        config = self.project.config.chains[self.chain_name]
        # TODO: how to do this without causing a circular dependency between these properties.
        # config.update({
        #     'registrar': self.registrar.address,
        # })
        return config

    has_registrar = True

    @cached_property
    def registrar(self):
        # deploy the registrar
        deploy_txn_hash = self.RegistrarFactory.deploy()
        registrar_address = self.wait.for_contract_address(deploy_txn_hash)

        return self.RegistrarFactory(address=registrar_address)

    full_reset = testrpc_fn_proxy('full_reset')
    reset = testrpc_fn_proxy('evm_reset')

    def snapshot(self, *args, **kwargs):
        return int(self.rpc_methods.evm_snapshot(*args, **kwargs), 16)

    revert = testrpc_fn_proxy('evm_revert')
    mine = testrpc_fn_proxy('evm_mine')

    _running = False

    def get_contract(self,
                     contract_name,
                     link_dependencies=None,
                     deploy_transaction=None,
                     deploy_args=None,
                     deploy_kwargs=None,
                     *args,
                     **kwargs):
        if contract_name not in self.contract_factories:
            raise UnknownContract(
                "No contract found with the name '{0}'.\n\n"
                "Available contracts are: {1}".format(
                    contract_name,
                    ', '.join((name for name in self.contract_factories.keys())),
                )
            )

        registrar = self.registrar
        contract_key = "contract/{name}".format(name=contract_name)
        if not registrar.call().exists(contract_key):
            # First dig down into the dependency tree to make the library
            # dependencies available.
            contract_bytecode = self.contract_factories[contract_name].code
            contract_dependencies = self._extract_library_dependencies(
                contract_bytecode, link_dependencies,
            )
            for dependency in contract_dependencies:
                self.get_contract(
                    dependency,
                    link_dependencies=link_dependencies,
                    *args,
                    **kwargs
                )

            # Then get the factory and deploy it.
            contract_factory = self.get_contract_factory(
                contract_name,
                link_dependencies=kwargs.get('link_dependencies'),
            )
            deploy_txn_hash = contract_factory.deploy(
                transaction=deploy_transaction,
                args=deploy_args,
                kwargs=deploy_kwargs,
            )
            contract_address = self.wait.for_contract_address(deploy_txn_hash)

            # Then register the address with the registrar so that the super
            # method will be able to get and return it.
            register_txn_hash = registrar.transact().setAddress(
                contract_key,
                contract_address,
            )
            self.wait.for_receipt(register_txn_hash)
        return super(BaseTesterChain, self).get_contract(
            contract_name,
            link_dependencies=link_dependencies,
            *args,
            **kwargs
        )


class TestRPCChain(BaseTesterChain):
    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        if self.port is None:
            self.port = get_open_port()

        self.provider = TestRPCProvider(port=self.port)
        self.rpc_methods = self.provider.server.application.rpc_methods

        self.rpc_methods.full_reset()
        self.rpc_methods.rpc_configure('eth_mining', False)
        self.rpc_methods.rpc_configure('eth_protocolVersion', '0x3f')
        self.rpc_methods.rpc_configure('net_version', 1)
        self.rpc_methods.evm_mine()

        wait_for_connection('127.0.0.1', self.port)
        self._running = True
        return self

    def __exit__(self, *exc_info):
        if not self._running:
            raise ValueError("The TesterChain is not running")
        try:
            self.provider.server.stop()
            self.provider.server.close()
            self.provider.thread.kill()
        finally:
            self._running = False


class EthereumTesterChain(BaseTesterChain):
    def __enter__(self):
        if self._running:
            raise ValueError("The TesterChain is already running")

        self.provider = EthereumTesterProvider()
        self.rpc_methods = self.provider.rpc_methods

        self.rpc_methods.full_reset()
        self.rpc_methods.rpc_configure('eth_mining', False)
        self.rpc_methods.rpc_configure('eth_protocolVersion', '0x3f')
        self.rpc_methods.rpc_configure('net_version', 1)
        self.rpc_methods.evm_mine()

        self._running = True
        return self

    def __exit__(self, *exc_info):
        if not self._running:
            raise ValueError("The TesterChain is not running")
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
            elif issubclass(self.provider_class, RPCProvider):
                provider = RPCProvider(port=self.geth.rpc_port)
            else:
                raise NotImplementedError(
                    "Unsupported provider class {0!r}.  Must be one of "
                    "IPCProvider or RPCProvider"
                )
            _web3 = Web3(provider)

            if 'default_account' in self.chain_config:
                _web3.eth.defaultAccount = self.chain_config['default_account']

            self._web3 = _web3
        return self._web3

    @property
    def chain_config(self):
        return self.project.config.chains[self.chain_name]

    @property
    def has_registrar(self):
        return 'registrar' in self.chain_config

    @cached_property
    def registrar(self):
        if not self.has_registrar:
            raise KeyError(
                "The configuration for the {0} chain does not include a "
                "registrar.  Please set this value to the address of the "
                "deployed registrar contract.".format(self.chain_name)
            )
        return get_registrar(
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

    has_registrar = True

    @cached_property
    def registrar(self):
        RegistrarFactory = get_registrar(self.web3)
        deploy_txn_hash = RegistrarFactory.deploy()
        registrar_address = self.wait.for_contract_address(deploy_txn_hash)
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
