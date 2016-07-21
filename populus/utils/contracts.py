import itertools
import os
import json
import re
import functools

import toposort

from .formatting import (
    remove_0x_prefix,
)
from .filesystem import (
    get_compiled_contracts_destination_path,
)


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


def load_compiled_contract_json(project_dir):
    compiled_contracts_path = get_compiled_contracts_destination_path(project_dir)

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


def find_link_references(bytecode):
    return set(DEPENDENCY_RE.findall(bytecode))


def link_contract_dependency(code, dependency_name, dependency_address):
    link_reference_re = re.compile(
        dependency_name[:36].ljust(38, "_").rjust(40, "_"),
    )
    linked_code = link_reference_re.sub(
        remove_0x_prefix(dependency_address),
        code,
    )
    return linked_code


def get_dependency_graph(contracts):
    expand_fn = functools.partial(
        expand_shortened_reference_name,
        full_names=set(contracts.keys()),
    )

    dependencies = {
        contract_name: {expand_fn(n) for n in find_link_references(contract_data['code'])}
        for contract_name, contract_data
        in contracts.items()
        if contract_data.get('code') is not None
    }
    return dependencies


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
        raise ValueError("Multiple candidates for name")
    else:
        raise ValueError("No valid names found")


def get_contract_deploy_order(dependency_graph):
    return toposort.toposort_flatten(dependency_graph)


def get_all_contract_dependencies(contract_name, dependency_graph):
    """
    Recursive computation of the linker dependencies for a specific contract
    within a contract dependency graph.
    """
    return set(itertools.chain(
        dependency_graph.get(contract_name, set()), *(
            get_all_contract_dependencies(dep, dependency_graph)
            for dep in dependency_graph.get(contract_name, set())
        )
    ))
