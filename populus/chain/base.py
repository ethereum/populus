from __future__ import absolute_import

import warnings

from pylru import lrucache

from eth_utils import (
    to_ordered_dict,
)

from populus.config.backend import (
    ContractBackendConfig,
)

from populus.contracts.provider import (
    Provider,
)
from populus.contracts.registrar import (
    Registrar,
)
from populus.wait import (
    Wait,
)

from populus.utils.config import (
    sort_prioritized_configs,
)
from populus.utils.contracts import (
    construct_contract_factories,
    package_contracts,
)
from populus.utils.functional import (
    cached_property,
)
from populus.utils.module_loading import (
    import_string,
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
    # Running the chain
    #
    _running = None

    def __enter__(self):
        self._running = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._running = False

    #
    # Required Public API
    #
    def get_web3_config(self):
        """
        Return the config object for the web3 instance used by this chain.
        """
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

    #
    # +--------------+
    # | Contract API |
    # +--------------+
    #
    @property
    @to_ordered_dict
    def contract_backend_configs(self):
        backend_configs = self.config.get_config('contracts.backends')
        sorted_backend_configs = sort_prioritized_configs(
            backend_configs,
            self.project.config
        )
        for backend_name, base_backend_config in sorted_backend_configs.items():
            yield backend_name, ContractBackendConfig(base_backend_config)

    @cached_property
    @to_ordered_dict
    def contract_backends(self):
        for backend_name, backend_config in self.contract_backend_configs.items():
            ProviderBackendClass = import_string(backend_config['class'])
            yield (
                backend_name,
                ProviderBackendClass(self, backend_config.get_config('settings')),
            )

    #
    # Provider
    #
    @property
    @to_ordered_dict
    def provider_backends(self):
        for backend_name, backend in self.contract_backends.items():
            if backend.is_provider:
                yield backend_name, backend

    @property
    def provider(self):
        if not self.provider_backends:
            raise ValueError(
                "Must have at least one provider backend "
                "configured\n{0}".format(self.contract_backend_configs)
            )
        return Provider(self, self.provider_backends)

    #
    # Registrar
    #
    @cached_property
    @to_ordered_dict
    def registrar_backends(self):
        for backend_name, backend in self.contract_backends.items():
            if backend.is_registrar:
                yield backend_name, backend

    @property
    def registrar(self):
        if not self.registrar_backends:
            raise ValueError(
                "Must have at least one registrar backend "
                "configured\n{0}".format(self.contract_backend_configs)
            )
        return Registrar(self, self.registrar_backends)

    #
    # !!!! Deprecated !!!!
    #
    @cached_property
    def contract_factories(self):
        warnings.warn(DeprecationWarning(
            "The `contract_factories` property has been deprecated.  Please use "
            "the `chain.provider` and `chain.provider` API to access contract "
            "factory data"
        ))
        compiled_contracts = self.project.compiled_contracts

        return construct_contract_factories(
            self.web3,
            compiled_contracts,
        )

    def get_contract_factory(self, contract_identifier, link_dependencies=None):
        warnings.warn(DeprecationWarning(
            "The `get_contract_factory` API has been relocated to "
            "`chain.provider.get_contract_factory`.  Please update your code to "
            "use this new API.  The `chain.get_contract_factory` API will be "
            "removed in subsequent releases."
        ))
        if link_dependencies is not None:
            raise DeprecationWarning(
                "The `link_dependencies` keyword has been deprecated.  To "
                "manually provide link addresses they should be loaded into the "
                "`Memory` contract backend prior to linking"
            )
        return self.provider.get_contract_factory(contract_identifier)

    def is_contract_available(self,
                              contract_identifier,
                              link_dependencies=None,
                              validate_bytecode=None,
                              raise_on_error=None):
        warnings.warn(DeprecationWarning(
            "The `is_contract_available` API has been relocated to "
            "`chain.provider.is_contract_available`.  Please update your code to "
            "use this new API.  The `chain.is_contract_available` API will be "
            "removed in subsequent releases."
        ))
        uses_deprecated_args = any((
            link_dependencies is not None,
            validate_bytecode is not None,
            raise_on_error is not None,
        ))
        if uses_deprecated_args:
            raise DeprecationWarning(
                "The `link_dependencies`, `validate_bytecode` and "
                "`raise_on_error` keywords have been deprecated.\n- To manually "
                "provide link addresses they should be loaded into the Memory` "
                "contract backend prior to linking.\n- Bytecode validation is no "
                "longer optional.\n- This method no longer raises exceptions."
            )
        return self.provider.is_contract_available(contract_identifier)

    def get_contract(self, contract_identifier, link_dependencies=None, validate_bytecode=None):
        warnings.warn(DeprecationWarning(
            "The `get_contract` API has been relocated to "
            "`chain.provider.get_contract`.  Please update your code to "
            "use this new API.  The `chain.get_contract` API will be "
            "removed in subsequent releases."
        ))
        if link_dependencies is not None or validate_bytecode is not None:
            raise DeprecationWarning(
                "The `link_dependencies` and `validate_bytecode` keywords have "
                "been deprecated.\n- To manually "
                "provide link addresses they should be loaded into the Memory` "
                "contract backend prior to linking.\n- Bytecode validation is no "
                "longer optional."
            )
        return self.provider.get_contract(contract_identifier)

    @property
    def deployed_contracts(self):
        warnings.warn(DeprecationWarning(
            "The `deployed_contracts` API has been relocated to "
            "`chain.provider.deployed_contracts`.  Please update your code to "
            "use this new API.  The `chain.deployed_contracts` API will be "
            "removed in subsequent releases."
        ))
        contract_classes = {
            contract_identifier: self.provider.get_contract(contract_identifier)
            for contract_identifier
            in self.provider.get_all_contract_names()
            if self.provider.is_contract_available(contract_identifier)
        }
        return package_contracts(contract_classes)
