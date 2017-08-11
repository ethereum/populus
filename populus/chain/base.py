from __future__ import absolute_import

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

from populus.config.helpers import (
    sort_prioritized_configs,
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
        if not self._running:
            raise ValueError("The Chain is not running")
        self._running = False

    #
    # Chain Interaction API
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
