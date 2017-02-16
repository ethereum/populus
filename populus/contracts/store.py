import itertools

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

    def __init__(self, store, store_backends):
        self.store = store
        self.store_backends = store_backends

    #
    # Store API
    #
    def get_base_contract_factory(self, contract_identifier):
        return get_base_contract_factory(contract_identifier, self.store_backends)

    def get_all_contract_data(self):
        return dict(itertools.chain.from_iterable(
            backend.get_all_contract_data().items()
            for backend
            in self.store_backends.values()
        ))

    def get_all_contract_names(self):
        return set(itertools.chain.from_iterable(
            backend.get_all_contract_names()
            for backend
            in self.store_backends.values()
        ))
