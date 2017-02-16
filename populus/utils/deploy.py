import itertools
from collections import OrderedDict

import toposort

from populus.utils.contracts import (
    get_shallow_dependency_graph,
    get_recursive_contract_dependencies,
)


def compute_deploy_order(dependency_graph):
    """
    Given a dictionary that maps contract names to their link dependencies,
    determine the overall dependency ordering for that set of contracts.
    """
    return toposort.toposort_flatten(dependency_graph)


def get_deploy_order(contracts_to_deploy, compiled_contracts):
    # Extract and dependencies that exist due to library linking.
    dependency_graph = get_shallow_dependency_graph(compiled_contracts)
    global_deploy_order = compute_deploy_order(dependency_graph)

    # Compute the full set of dependencies needed to deploy the desired
    # contracts.
    all_deploy_dependencies = set(itertools.chain.from_iterable(
        get_recursive_contract_dependencies(contract_name, dependency_graph)
        for contract_name in contracts_to_deploy
    ))
    all_contracts_to_deploy = all_deploy_dependencies.union(contracts_to_deploy)

    # Now compute the order that the contracts should be deployed based on
    # their dependencies.
    deploy_order = [
        (contract_name, compiled_contracts[contract_name])
        for contract_name
        in global_deploy_order
        if contract_name in all_contracts_to_deploy
    ]
    return OrderedDict(deploy_order)
