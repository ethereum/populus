from __future__ import absolute_import

import warnings

from pylru import lrucache

from populus.utils.contracts import (
    construct_contract_factories,
)
from populus.utils.functional import (
    cached_property,
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
    # !!!! Deprecated !!!!
    #
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

    def get_contract_factory(self, contract_identifier):
        pass

    def is_contract_available(self, contract_identifier):
        pass

    def are_contract_factory_dependencies_available(self, contract_identifier):
        pass

    def get_contract(self, contract_identifier):
        pass

    def get_or_deploy_contract(self,
                               contract_identifier,
                               deploy_transaction=None,
                               deploy_args=None,
                               deploy_kwargs=None):
        """
        Same as get_contract but it will also lazily deploy the contract with
        the provided deployment arguments
        """
        pass

    def get_contract_address(self, contract_identifier):
        """
        Retrieve a contract address from the provider backends.
        """
        pass

    @property
    def deployed_contracts(self):
        pass
