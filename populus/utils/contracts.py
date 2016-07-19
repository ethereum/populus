import itertools
import operator
import functools


def merge_dependencies(*dependencies):
    """
    Takes dictionaries of key => set(...) and merges them all into a single
    dictionary where each key is the union of all of the sets for that key
    across all dictionaries.
    """
    return {
        k: set(functools.reduce(
            operator.or_,
            (d.get(k, set()) for d in dependencies)
        ))
        for k in itertools.chain.from_iterable((d.keys() for d in dependencies))
    }


def get_dependencies(contract_name, dependencies):
    return set(itertools.chain(
        dependencies.get(contract_name, set()), *(
            get_dependencies(dep, dependencies)
            for dep in dependencies.get(contract_name, set())
        )
    ))


def package_contracts(web3, contracts):
    # TODO: fix this
    contract_classes = {
        name: web3.eth.contract(**contract_data) for name, contract_data in contracts.items()
    }

    _dict = {
        '__len__': lambda s: len(contract_classes),
        '__iter__': lambda s: iter(contract_classes.items()),
        '__getitem__': lambda s, k: contract_classes.__getitem__[k],
    }
    _dict.update(contract_classes)

    return type('contracts', (object,), _dict)()
