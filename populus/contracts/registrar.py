import functools
import itertools

from eth_utils import (
    to_tuple,
)

from populus.utils.contracts import (
    EMPTY_BYTECODE_VALUES,
    find_deploy_block_number,
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
        found_addresses = self._get_contract_addresses_from_backends(contract_identifier)
        if not found_addresses:
            raise NoKnownAddress("No known address for contract")

        addresses_with_code = tuple(
            address
            for address
            in found_addresses
            if self.chain.web3.eth.getCode(address) not in EMPTY_BYTECODE_VALUES
        )
        empty_addresses = tuple(
            address
            for address
            in found_addresses
            if self.chain.web3.eth.getCode(address) in EMPTY_BYTECODE_VALUES
        )
        sorted_addresses = tuple(sorted(
            set(addresses_with_code),
            key=functools.partial(find_deploy_block_number, self.chain.web3),
            reverse=True,
        ))
        known_addresses = tuple(itertools.chain(
            sorted_addresses,
            empty_addresses,
        ))

        return known_addresses

    @to_tuple
    @chain_return
    def _get_contract_addresses_from_backends(self, contract_identifier):
        for registrar in self.registrar_backends.values():
            try:
                yield registrar.get_contract_addresses(contract_identifier)
            except NoKnownAddress:
                continue
