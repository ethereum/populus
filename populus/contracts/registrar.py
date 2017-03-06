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

    @to_tuple
    @chain_return
    def get_contract_addresses(self, contract_identifier):
        """
        Retrieve a contract address from the registrar
        """
        # TODO: this should really evaluate *all* addresses returned and then
        # figure out if any of them are the correct addresses.
        for registrar in self.registrar_backends.values():
            try:
                yield registrar.get_contract_addresses(contract_identifier)
            except NoKnownAddress:
                continue
        else:
            raise NoKnownAddress("No known address for contract")
