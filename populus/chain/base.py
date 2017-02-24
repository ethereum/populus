import warnings

from __future__ import absolute_import
import itertools

from pylru import lrucache

from populus.legacy.contracts import (
    get_contract_library_dependencies,
)

from populus.contracts.exceptions import (
    NoKnownAddress,
    BytecodeMismatchError,
    UnknownContract,
)

from populus.utils.contracts import (
    construct_contract_factories,
    package_contracts,
)
from populus.utils.functional import (
    cached_property,
)
from populus.utils.linking import (
    link_bytecode_by_name,
)
from populus.utils.wait import (
    Wait,
)


class BaseChain(object):
    """
    Base class for how populus interacts with the blockchain.

    :param project: Instance of :class:`populus.project.Project`
    """
    project = None
    chain_name = None
    config = None
    _factory_cache = None

    def __init__(self, project, chain_name, chain_config):
        self.project = project
        self.chain_name = chain_name
        self.config = chain_config
        self._factory_cache = lrucache(128)
        self.initialize_chain()

    def initialize_chain(self):
        """
        Hook for initialization that is called during class instantiation.
        """
        pass

    #
    # Required Public API
    #
    def get_web3_config(self):
        web3_config = self.config.get_web3_config()
        return web3_config

    @property
    def web3_config(self):
        return self.get_web3_config()

    @cached_property
    def web3(self):
        if not self._running:
            raise ValueError("Chain must be running prior to accessing web3")
        return self.web3_config.get_web3()

    @property
    def wait(self):
        return Wait(self.web3)

    @cached_property
    def contract_factories(self):
        warnings.warn(DeprecationWarning(
            "The `contract_factories` property has been deprecated.  Please use "
            "the `chain.store` and `chain.provider` API to access contract "
            "factory data"
        ))
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

    #
    # Running the chain
    #
    _running = None

    def __enter__(self):
        self._running = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._running = False

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
            link_bytecode_by_name(bytecode, **all_link_dependencies)
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

        is_bytecode_match = chain_bytecode == contract_factory.bytecode_runtime
        if not is_bytecode_match and raise_on_error:
            raise BytecodeMismatchError(
                "Bytecode @ {0} does not match expected contract bytecode.\n\n"
                "expected : '{1}'\n"
                "actual   : '{2}'\n".format(
                    contract_address,
                    contract_factory.bytecode_runtime,
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
            bytecode, bytecode_runtime = self._link_code(
                bytecodes=[
                    base_contract_factory.bytecode,
                    base_contract_factory.bytecode_runtime,
                ],
                link_dependencies=link_dependencies,
            )
        else:
            bytecode, bytecode_runtime = (
                base_contract_factory.bytecode,
                base_contract_factory.bytecode_runtime,
            )

        contract_factory = self.web3.eth.contract(
            bytecode=bytecode,
            bytecode_runtime=bytecode_runtime,
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


def testrpc_fn_proxy(fn_name):
    def inner(self, *args, **kwargs):
        fn = getattr(self.rpc_methods, fn_name)
        return fn(*args, **kwargs)
    inner.__name__ = fn_name
    return inner


class BaseTesterChain(BaseChain):
    provider = None

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
            contract_bytecode = self.contract_factories[contract_name].bytecode
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
