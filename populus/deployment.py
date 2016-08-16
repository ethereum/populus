import itertools

from web3.utils.formatting import (
    remove_0x_prefix,
)

from populus.utils.contracts import (
    get_shallow_dependency_graph,
    get_contract_deploy_order,
    get_recursive_contract_dependencies,
    link_contract,
    package_contracts,
)

from populus.utils.transactions import (
    get_contract_address_from_txn,
)


def deploy_contracts(web3,
                     all_contracts,
                     contracts_to_deploy=None,
                     txn_defaults=None,
                     constructor_args=None,
                     contract_addresses=None,
                     timeout=120):
    """
    Do a full synchronous deploy of all project contracts or a subset of the
    contracts.

    1. Wait for whatever block number was specified (in
    """
    deploy_transactions = {}

    if contract_addresses is None:
        contract_addresses = {}

    if constructor_args is None:
        constructor_args = {}

    if txn_defaults is None:
        txn_defaults = {}

    if not contracts_to_deploy:
        contracts_to_deploy = tuple(all_contracts.keys())

    # Extract and dependencies that exist due to library linking.
    dependency_graph = get_shallow_dependency_graph(all_contracts)

    # If a subset of contracts have been specified to be deployed compute
    # any dependencies that also need to be deployed.
    all_deploy_dependencies = set(itertools.chain.from_iterable(
        get_recursive_contract_dependencies(contract_name, dependency_graph)
        for contract_name in contracts_to_deploy
    ))
    all_contracts_to_deploy = all_deploy_dependencies.union(contracts_to_deploy)

    # Now compute the order that the contracts should be deployed based on
    # their dependencies.
    deploy_order = [
        (contract_name, all_contracts[contract_name])
        for contract_name
        in get_contract_deploy_order(dependency_graph)
        if contract_name in all_contracts_to_deploy
    ]

    # Validate that all contracts are deployable meaning they have `code`
    # associated with them.
    undeployable_contracts = [
        contract_name
        for contract_name, _ in deploy_order
        if not remove_0x_prefix(all_contracts[contract_name].get('code'))
    ]

    if undeployable_contracts:
        raise ValueError("Some contracts do not have code and thus cannot be deployed")

    for contract_name, contract_data in deploy_order:
        # if the contract has dependencies then link the code.
        if dependency_graph[contract_name]:
            code = link_contract(contract_data['code'], **contract_addresses)
        else:
            code = contract_data['code']

        contract = web3.eth.contract(
            abi=contract_data['abi'],
            code=code,
        )

        args = constructor_args.get(contract_name, [])
        if callable(args):
            args = args(contract_addresses)

        txn = dict(**txn_defaults)

        deploy_txn = contract.deploy(txn, args)

        contract_addresses[contract_name] = get_contract_address_from_txn(
            web3,
            deploy_txn,
            timeout=timeout,
        )
        deploy_transactions[contract_name] = deploy_txn

    package_data = {
        contract_name: dict(
            address=contract_addresses[contract_name],
            **all_contracts[contract_name]
        )
        for contract_name in contract_addresses
    }

    contracts = package_contracts(web3, package_data)
    for contract_name, contract in contracts:
        contract.deploy_txn_hash = deploy_transactions[contract_name]

    return contracts


def validate_deployed_contracts(web3, contracts):
    for _, contract in contracts:
        code = web3.eth.getCode(contract.address)
        if len(code) <= 2:
            raise ValueError("Looks like a contract failed to deploy")
