import itertools
from collections import OrderedDict

import toposort

from populus.utils.contracts import (
    get_shallow_dependency_graph,
    get_recursive_contract_dependencies,
)
from populus.utils.linking import (
    link_bytecode_by_name,
)


def compute_deploy_order(dependency_graph):
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


def deploy_contract(chain,
                    contract_name,
                    contract_factory=None,
                    deploy_transaction=None,
                    deploy_arguments=None,
                    link_dependencies=None):
    if contract_factory is None:
        contract_factory = chain.contract_factories[contract_name]

    web3 = chain.web3

    bytecode = link_bytecode_by_name(contract_factory.bytecode, **link_dependencies)

    if contract_factory.bytecode_runtime:
        bytecode_runtime = link_bytecode_by_name(
            contract_factory.bytecode_runtime,
            **link_dependencies
        )
    else:
        bytecode_runtime = None

    ContractFactory = web3.eth.contract(
        abi=contract_factory.abi,
        bytecode=bytecode,
        bytecode_runtime=bytecode_runtime,
        source=contract_factory.source,
    )

    deploy_transaction_hash = ContractFactory.deploy(
        deploy_transaction,
        deploy_arguments,
    )
    return deploy_transaction_hash, ContractFactory
