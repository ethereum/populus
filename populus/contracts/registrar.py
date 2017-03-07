from eth_utils import (
    to_tuple,
)

from populus.utils.functional import chain_return

from .exceptions import (
    NoKnownAddress,
)


class Registrar(object):
    """
    Abstraction for recording known contracts on a given chain.
    """
    registrar_backends = None

    def __init__(self, chain, registrar_backends):
        self.chain = chain
        self.registrar_backends = registrar_backends

    def set_contract_address(self, contract_name, contract_address):
        """
        Set a contract address in the registrar
        """
        return [
            registrar.set_contract_address(contract_name, contract_address)
            for registrar in self.registrar_backends.values()
        ]

    def get_contract_addresses(self, contract_identifier):
        """
        Retrieve a contract address from the registrar
        """
        known_addresses = self._get_contract_addresses_from_backends(contract_identifier)
        if not known_addresses:
            raise NoKnownAddress("No known address for contract")
        return known_addresses

    @to_tuple
    @chain_return
    def _get_contract_addresses_from_backends(self, contract_identifier):
        for registrar in self.registrar_backends.values():
            try:
                yield registrar.get_contract_addresses(contract_identifier)
            except NoKnownAddress:
                continue
