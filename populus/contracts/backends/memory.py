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
    is_provider = False

    contract_addresses = None

    def setup_backend(self):
        self.contract_addresses = {}

    #
    # Registrar API
    #
    def get_contract_addresses(self, instance_name):
        if instance_name in self.contract_addresses:
            return self.contract_addresses[instance_name]
        else:
            raise NoKnownAddress("No known address for '{0}'".format(instance_name))

    def set_contract_address(self, instance_name, address):
        if instance_name in self.contract_addresses:
            self.contract_addresses[instance_name].add(address)
        else:
            self.contract_addresses[instance_name] = {address}
