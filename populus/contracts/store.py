import itertools

from pylru import lrucache

from populus.utils.linking import (
    link_bytecode,
    find_link_references,
)

from .exceptions import (
    UnknownContract,
)


def get_base_contract_factory(contract_identifier, store_backends):
    for _, backend in store_backends.items():
        try:
            return backend.get_base_contract_factory(contract_identifier)
        except UnknownContract:
            pass
    else:
        raise UnknownContract(
            "No contract data was available for the contract identifier '{0}' "
            "from any of the configured backends".format(contract_identifier)
        )


class Store(object):
    """
    Abstraction for retrieving contracts on a given chain.
    """
    store_backends = None

    def __init__(self, chain, store_backends):
        self.chain = chain
        self.store_backends = store_backends
        self._factory_cache = lrucache(128)

    #
    # Store API
    #
    def get_base_contract_factory(self, contract_identifier):
        """
        Returns the base contract factory for the given `contract_identifier`.
        The `bytecode` and `bytecode_runtime` will be unlinked in this class.
        """
        return get_base_contract_factory(contract_identifier, self.store_backends)

    def get_contract_data(self, contract_identifier):
        """
        Returns a dictionary containing the compiler output for the given
        contract identifier.
        """
        for backend in self.store_backends.value():
            try:
                return backend.get_contract_data(contract_identifier)
            except UnknownContract:
                continue
        else:
            raise UnknownContract(
                "No contracts found for the contract identifier '{0}'".format(
                    contract_identifier,
                )
            )

    def get_all_contract_data(self):
        """
        Returns a dictionary mapping all contract identifiers to their contract data.
        """
        return dict(itertools.chain.from_iterable(
            backend.get_all_contract_data().items()
            for backend
            in self.store_backends.values()
        ))

    def get_all_contract_names(self):
        """
        Returns a set of all of the known contract identifiers.
        """
        return set(itertools.chain.from_iterable(
            backend.get_all_contract_names()
            for backend
            in self.store_backends.values()
        ))

    def get_contract_factory(self, contract_identifier):
        """
        Returns the contract factory for the given `contract_identifier`.  The
        `bytecode` and `bytecode_runtime` values for this factory will be fully
        linked.
        """
        if contract_identifier in self._factory_cache:
            return self._factory_cache[contract_identifier]

        BaseContractFactory = self.get_base_contract_factory(contract_identifier)

        bytecode = self.link_bytecode(BaseContractFactory.bytecode)
        bytecode_runtime = self.link_bytecode(BaseContractFactory.bytecode_runtime)

        ContractFactory = BaseContractFactory.factory(
            web3=BaseContractFactory.web3,
            bytecode=bytecode,
            bytecode_runtime=bytecode_runtime,
        )

        self._factory_cache[contract_identifier] = ContractFactory
        return ContractFactory

    #
    # Private API
    #
    def link_bytecode(self, bytecode):
        """
        Return the fully linked contract bytecode.

        Note: This *must* use `get_contract` and **not** `get_contract_address`
        for resolution of link dependencies.  If it merely uses
        `get_contract_address` then the bytecode of sub-dependencies is not
        verified.
        """
        resolved_link_references = tuple((
            (link_reference, self.chain.provider.get_contract(link_reference.full_name).address)
            for link_reference
            in find_link_references(
                bytecode,
                self.get_all_contract_names(),
            )
        ))

        linked_bytecode = link_bytecode(bytecode, resolved_link_references)
        return linked_bytecode
