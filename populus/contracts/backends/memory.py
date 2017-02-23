from populus.contracts.exceptions import (
    NoKnownAddress,
)

from .base import BaseContractBackend


class MemoryBackend(BaseContractBackend):
    """
    A contract backend that only acts as a provider sourcing contracts from
    installed packages.
    """
    is_registrar = True
    is_provider = True
    is_store = False

    contract_addresses = None

    def setup_backend(self):
        self.contract_addresses = {}

    #
    # ProviderAPI
    #
    def get_contract_address(self, instance_name):
        try:
            return self.contract_addresses[instance_name]
        except KeyError:
            raise NoKnownAddress("No known address for '{0}'".format(instance_name))

    #
    # Private API
    #
    def set_contract_address(self, instance_name, address):
        self.contract_addresses[instance_name] = address
