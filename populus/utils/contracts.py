import itertools
import os
import json
import re
import functools

import toposort

from web3.utils.formatting import (
    remove_0x_prefix,
)
from web3.utils.string import (
    coerce_args_to_text,
)

from populus.utils.functional import (
    compose,
)
from .filesystem import (
    get_compiled_contracts_file_path,
)


def package_contracts(contract_classes):
    _dict = {
        '__len__': lambda s: len(contract_classes),
        '__iter__': lambda s: iter(contract_classes.items()),
        '__contains__': lambda s, k: contract_classes.__contains__(k),
        '__getitem__': lambda s, k: contract_classes.__getitem__(k),
        '__setitem__': lambda s, k, v: contract_classes.__setitem__(k, v),
        'keys': lambda s: contract_classes.keys(),
        'values': lambda s: contract_classes.values(),
    }
    _dict.update(contract_classes)

    return type('contracts', (object,), _dict)()


def construct_contract_factories(web3, contracts):
    constructor_kwargs = {
        contract_name: {
            'code': contract_data.get('code'),
            'code_runtime': contract_data.get('code_runtime'),
            'abi': contract_data.get('abi'),
            'source': contract_data.get('source'),
            'address': contract_data.get('address'),
        } for contract_name, contract_data in contracts.items()
    }
    contract_classes = {
        name: web3.eth.contract(**contract_data)
        for name, contract_data in constructor_kwargs.items()
    }
    return package_contracts(contract_classes)


def load_compiled_contract_json(project_dir):
    compiled_contracts_path = get_compiled_contracts_file_path(project_dir)

    if not os.path.exists(compiled_contracts_path):
        raise ValueError("No compiled contracts found")

    with open(compiled_contracts_path) as contracts_file:
        contracts = json.loads(contracts_file.read())

    return contracts


DEPENDENCY_RE = re.compile((
    '__'  # Prefixed by double underscore
    '(?P<name>[a-zA-Z_](?:[a-zA-Z0-9_]{0,34}[a-zA-Z0-9])?)'  # capture the name of the dependency
    '_{0,35}'
    '__'  # End with a double underscore
))


@coerce_args_to_text
def find_link_references(bytecode):
    """
    Given bytecode, this will return all of the unlinked references from within
    the bytecode.

    The returned names may be truncated to 36 characters.
    """
    return set(DEPENDENCY_RE.findall(bytecode))


def make_link_regex(contract_name):
    """
    Returns a regex that will match embedded link references within a
    contract's bytecode.
    """
    return re.compile(
        contract_name[:36].ljust(38, "_").rjust(40, "_")
    )


def expand_shortened_reference_name(name, full_names):
    """
    If a contract dependency has a name longer than 36 characters then the name
    is truncated in the compiled but unlinked bytecode.  This maps a name to
    it's full name.
    """
    if name in full_names:
        return name

    candidates = [
        n for n in full_names if n.startswith(name)
    ]
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        raise ValueError(
            "Multiple candidates found trying to expand '{0}'.  Found '{1}'. "
            "Searched '{2}'".format(
                name,
                ','.join(candidates),
                ','.join(full_names),
            )
        )
    else:
        raise ValueError(
            "Unable to expand '{0}'. "
            "Searched '{1}'".format(
                name,
                ','.join(full_names),
            )
        )


def link_bytecode(bytecode, **dependencies):
    """
    Given the bytecode for a contract, and it's dependencies in the form of
    {contract_name: address} this functino returns the bytecode with all of the
    link references replaced with the dependency addresses.
    """
    linker_fn = compose(*(
        functools.partial(
            make_link_regex(name).sub,
            remove_0x_prefix(address),
        )
        for name, address in dependencies.items()
    ))
    linked_bytecode = linker_fn(bytecode)
    return linked_bytecode


def get_contract_library_dependencies(bytecode, full_contract_names):
    """
    Given a contract bytecode and an iterable of all of the known full names of
    contracts, returns a set of the contract names that this contract bytecode
    depends on.

    To get the full dependency graph use the `get_recursive_contract_dependencies`
    function.
    """
    expand_fn = functools.partial(
        expand_shortened_reference_name,
        full_names=full_contract_names,
    )
    return {
        expand_fn(name) for name in find_link_references(bytecode)
    }


def get_shallow_dependency_graph(contracts):
    """
    Given a dictionary of compiled contract data, this returns a *shallow*
    dependency graph of each contracts explicit link dependencies.
    """
    dependencies = {
        contract_name: get_contract_library_dependencies(
            contract_data['code'],
            contracts.keys(),
        )
        for contract_name, contract_data
        in contracts.items()
        if contract_data.get('code') is not None
    }
    return dependencies


def get_contract_deploy_order(dependency_graph):
    return toposort.toposort_flatten(dependency_graph)


def get_recursive_contract_dependencies(contract_name, dependency_graph):
    """
    Recursive computation of the linker dependencies for a specific contract
    within a contract dependency graph.
    """
    return set(itertools.chain(
        dependency_graph.get(contract_name, set()), *(
            get_recursive_contract_dependencies(dep, dependency_graph)
            for dep in dependency_graph.get(contract_name, set())
        )
    ))
