import itertools

from eth_utils import (
    to_tuple,
    flatten_return,
)

from populus.utils.contracts import (
    EMPTY_BYTECODE_VALUES,
)

from .exceptions import (
    NoKnownAddress,
)


class Registrar(object):
    """
    Abstraction for recording known contracts on a given chain.
    """
    registrar_backends = None

    def __init__(self, web3, registrar_backends):
        self.web3 = web3
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
        found_contract_address_meta = self._get_contract_addresses_from_backends(
            contract_identifier
        )
        if not found_contract_address_meta:
            raise NoKnownAddress("No known address for contract")
        if len(found_contract_address_meta) == 1:
            return found_contract_address_meta[0].address,

        addresses_with_code = tuple(set(
            contract_address_meta.address
            for contract_address_meta
            in found_contract_address_meta
            if self.web3.eth.getCode(contract_address_meta.address) not in EMPTY_BYTECODE_VALUES
        ))
        empty_addresses = tuple(set(
            contract_address_meta.address
            for contract_address_meta
            in found_contract_address_meta
            if self.web3.eth.getCode(contract_address_meta.address) in EMPTY_BYTECODE_VALUES
        ))

        if len(addresses_with_code) > 1:
            sorted_addresses_meta = sorted(
                found_contract_address_meta,
                key=lambda x: getattr(x, 'timestamp'),
                reverse=True,
            )
            sorted_addresses = map(lambda x: x.address, sorted_addresses_meta)
        else:
            sorted_addresses = addresses_with_code

        known_addresses = tuple(itertools.chain(
            sorted_addresses,
            empty_addresses,
        ))

        return known_addresses

    @to_tuple
    @flatten_return
    def _get_contract_addresses_from_backends(self, contract_identifier):
        for registrar in self.registrar_backends.values():
            try:
                yield registrar.get_contract_addresses(contract_identifier)
            except NoKnownAddress:
                continue
