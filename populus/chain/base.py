from __future__ import absolute_import

import os
from pylru import lrucache

from eth_utils import (
    to_ordered_dict,
)

from populus.config.backend import (
    ContractBackendConfig,
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

    """

    chain_name = None
    chain_dir = None
    config = None
    _factory_cache = None

    def __init__(self, chain_name, chain_config, user_config, chain_dir=None):
        self.chain_name = chain_name
        self.config = chain_config
        self.user_config = user_config
        if chain_dir is None:
            self.chain_dir = os.path.join(
                os.path.expanduser("~"), chain_config.get("dir")
                )
        else:
            self.chain_dir = chain_dir
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
            self.user_config
            #self.project.config
        )
        for backend_name, base_backend_config in sorted_backend_configs.items():
            yield backend_name, ContractBackendConfig(base_backend_config)

    @cached_property
    @to_ordered_dict
    def contract_backends(self):
        for backend_name, backend_config in self.contract_backend_configs.items():
            ChainBackendClass = import_string(backend_config['class'])
            yield (
                backend_name,
                ChainBackendClass(backend_config.get_config('settings')),
            )