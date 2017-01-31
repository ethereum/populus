from populus.contracts.exceptions import NoKnownAddress

from .base import BaseContractBackend


class MemoryBackend(BaseContractBackend):
    """
    A contract backend that only acts as a provider sourcing contracts from
    installed packages.
    """
    contract_addresses = None

    def setup_backend(self):
        self.contract_addresses = {}

    @property
    def is_registrar(self):
        return True

    @property
    def is_provider(self):
        return True

    def get_contract_address(self, instance_name):
        try:
            return self.contract_addresses[instance_name]
        except KeyError:
            raise NoKnownAddress("No known address for '{0}'".format(instance_name))

    def set_contract_address(self, instance_name, address):
        self.contract_addresses[instance_name] = address
