from populus.utils.module_loading import (
    import_string,
)
from populus.utils.functional import (
    cached_property,
    cast_return_to_ordered_dict,
)
from populus.utils.config import (
    sort_prioritized_configs,
)

from .provider import (
    Provider,
)
from .registrar import (
    Registrar,
)


class ContractStore(object):
    chain = None

    def __init__(self, chain):
        self.chain = chain

    @property
    def backend_configs(self):
        config = self.chain.config.get_config('contracts.backends')
        return sort_prioritized_configs(config, self.chain.project.config)

    @cached_property
    @cast_return_to_ordered_dict
    def contract_backends(self):
        for backend_name, backend_config in self.backend_configs.items():
            ProviderBackendClass = import_string(backend_config['class'])
            yield (
                backend_name,
                ProviderBackendClass(self.chain, backend_config.get_config('settings')),
            )

    #
    # Provider
    #
    @property
    @cast_return_to_ordered_dict
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
        return Provider(self.chain, self.provider_backends)

    #
    # Registrar
    #
    @cached_property
    @cast_return_to_ordered_dict
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
        return Registrar(self.chain, self.registrar_backends)
