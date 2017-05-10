from populus.contracts.exceptions import (
    UnknownContract,
)
from populus.contracts.contract import (
    construct_contract_factory,
)


class BaseContractBackend(object):
    chain = None

    def __init__(self, chain, config):
        self.chain = chain
        self.config = config
        self.setup_backend()

    #
    # Meta API
    #
    @property
    def is_provider(self):
        raise NotImplementedError("Must be implemented by subclasses")

    @property
    def is_registrar(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def setup_backend(self):
        """
        Hook for subclasses to do backend initialization without having to
        override the `__init__` method.
        """
        pass

    #
    # Registrar API
    #
    def set_contract_address(self, instance_name, address):
        """
        Returns the address for the contract instance in the registrar.
        """
        raise NotImplementedError("Must be implemented by subclasses")

    def get_contract_addresses(self, instance_name):
        """
        Returns all known address of the requested contract instance.
        """
        raise NotImplementedError("Must be implemented by subclasses")

    #
    # Provider API
    #
    def get_contract_identifier(self, contract_name):
        """
        Given a contract name, return the contract identifier that will
        retrieve the appropriate the base contract factory.
        """
        raise NotImplementedError("Must be implemented by subclasses")

    def get_base_contract_factory(self, contract_name):
        """
        Returns the base contract factory for the given contract identifier.
        """
        try:
            contract_identifier = self.get_contract_identifier(contract_name)
        except KeyError:
            raise UnknownContract(
                "No contract available for the name '{0}'".format(
                    contract_name,
                )
            )

        contract_data = self.get_contract_data(contract_identifier)

        base_contract_factory = construct_contract_factory(
            chain=self.chain,
            contract_identifier=contract_identifier,
            contract_data=contract_data,
        )
        return base_contract_factory

    def get_all_contract_data(self):
        """
        Returns all contract data available from this backend.
        """
        raise NotImplementedError("Must be implemented by subclasses")

    def get_contract_data(self, contract_name):
        """
        Returns the raw contract data.
        """
        contract_identifier = self.get_contract_identifier(contract_name)
        try:
            return self.get_all_contract_data()[contract_identifier]
        except KeyError:
            raise UnknownContract(
                "No contract found for the name '{0}'".format(contract_name)
            )

    def get_all_contract_names(self):
        """
        Returns a set of all of the contract names for this backend.
        """
        return set(self.get_all_contract_data().keys())
