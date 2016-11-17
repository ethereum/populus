from populus.utils.functional import (
    cached_property,
)
from populus.utils.wait import (
    Wait,
)
from populus.utils.contracts import (
    construct_contract_factories,
)
from populus.utils.chains import (
    setup_web3_from_config,
)

from populus.contracts import (
    ContractStore,
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
    # Contract Store
    #
    @cached_property
    def store(self):
        return ContractStore(self)

    #
    # Contract Factories
    #
    @cached_property
    def base_contract_factories(self):
        return construct_contract_factories(
            self.web3,
            self.project.compiled_contract_data,
        )

    #
    # Context manager API
    #
    def __enter__(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
