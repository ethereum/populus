from collections import OrderedDict

from populus.utils.contracts import (
    get_shallow_dependency_graph,
    get_contract_deploy_order,
)


def get_dependency_order(compiled_contracts):
    # Extract and dependencies that exist due to library linking.
    dependency_graph = get_shallow_dependency_graph(compiled_contracts)

    # Now compute the order that the contracts should be deployed based on
    # their dependencies.
    deploy_order = [
        (contract_name, compiled_contracts[contract_name])
        for contract_name
        in get_contract_deploy_order(dependency_graph)
    ]
    return OrderedDict(deploy_order)
