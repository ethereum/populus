import itertools

import toposort

from populus.utils.contracts import (
    compute_direct_dependency_graph,
    compute_recursive_contract_dependencies,
)


def compute_deploy_order(dependency_graph):
    """
    Given a dictionary that maps contract to their dependencies,
    determine the overall dependency ordering for that set of contracts.
    """
    return toposort.toposort_flatten(dict(dependency_graph))


def get_deploy_order(contracts_to_deploy, compiled_contracts):
    # Extract and dependencies that exist due to library linking.
    dependency_graph = compute_direct_dependency_graph(compiled_contracts.values())
    global_deploy_order = compute_deploy_order(dependency_graph)

    # Compute the full set of dependencies needed to deploy the desired
    # contracts.
    all_deploy_dependencies = set(itertools.chain.from_iterable(
        compute_recursive_contract_dependencies(contract_name, dependency_graph)
        for contract_name in contracts_to_deploy
    ))
    all_contracts_to_deploy = all_deploy_dependencies.union(contracts_to_deploy)

    # Now compute the order that the contracts should be deployed based on
    # their dependencies.
    deploy_order = tuple(
        contract_name
        for contract_name
        in global_deploy_order
        if contract_name in all_contracts_to_deploy
    )
    return deploy_order
