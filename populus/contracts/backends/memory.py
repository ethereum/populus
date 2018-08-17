from populus.contracts.exceptions import (
    NoKnownAddress,
)
from populus.utils.datastructures import (
    ContractMeta,
    TimeStampedRegistrar,
)

from .base import BaseContractBackend


class MemoryBackend(BaseContractBackend):
    """
    A contract backend that only acts as a provider sourcing contracts from
    installed packages.
    """
    is_registrar = True
    is_provider = False

    contract_meta = None

    def setup_backend(self):
        self.contract_meta = TimeStampedRegistrar(ContractMeta)

    #
    # Registrar API
    #
    def get_contract_addresses(self, instance_name):
        if instance_name in self.contract_meta:
            return self.contract_meta[instance_name]
        else:
            raise NoKnownAddress("No known address for '{0}'".format(instance_name))

    def set_contract_address(self, instance_name, address):
        self.contract_meta.insert(instance_name, address)
