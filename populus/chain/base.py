from eth_utils import (
    to_ordered_dict,
)

from populus.contracts.provider import (
    Provider,
)
from populus.contracts.registrar import (
    Registrar,
)
from populus.contracts.store import (
    Store,
)

from populus.utils.chains import (
    setup_web3_from_config,
)
from populus.utils.config import (
    sort_prioritized_configs,
)
from populus.utils.functional import (
    cached_property,
)
from populus.utils.module_loading import (
    import_string,
)
from populus.utils.wait import (
    Wait,
)


class Chain(object):
    """
    Base class for how populus interacts with the blockchain.

    :param project: Instance of :class:`populus.project.Project`
    """
    project = None
    chain_name = None
    _factory_cache = None

    def __init__(self, project, chain_name, chain_config):
        self.project = project
        self.chain_name = chain_name
        self.config = chain_config
        self.initialize_chain()

    def initialize_chain(self):
        """
        Hook for initialization that will be called during class instantiation.
        """
        pass

    #
    # Context manager API
    #
    def __enter__(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    #
    # Chain Interaction API
    #
    def get_web3_config(self):
        web3_config = self.config.get_config('web3')

        if '$ref' in web3_config:
            return self.project.config.get_config(web3_config['$ref'])
        else:
            return web3_config

    @property
    def web3_config(self):
        return self.get_web3_config()

    @cached_property
    def web3(self):
        return setup_web3_from_config(self.web3_config)

    @property
    def wait(self):
        return Wait(self.web3)

    #
    # +--------------+
    # | Contract API |
    # +--------------+
    #
    @property
    def contract_backend_configs(self):
        config = self.config.get_config('contracts.backends')
        return sort_prioritized_configs(config, self.project.config)

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
                "configured\n{0}".format(self.backend_configs)
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
                "configured\n{0}".format(self.backend_configs)
            )
        return Registrar(self, self.registrar_backends)

    #
    # Source
    #
    @property
    @to_ordered_dict
    def store_backends(self):
        for backend_name, backend in self.contract_backends.items():
            if backend.is_store:
                yield backend_name, backend

    @property
    def store(self):
        if not self.store_backends:
            raise ValueError(
                "Must have at least one store backend "
                "configured\n{0}".format(self.backend_configs)
            )
        return Store(self, self.store_backends)
