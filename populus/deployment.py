import itertools
import copy
import toposort
import random
import gevent

from populus.utils.formatting import (
    remove_0x_prefix,
)
from populus.utils.contracts import (
    get_dependency_graph,
    get_contract_deploy_order,
)

from populus.utils.transaction import (
    get_contract_address_from_txn,
)


def deploy_contracts(web3,
                     all_contracts,
                     contracts_to_deploy=None,
                     transaction_defaults=None,
                     constructor_args=None,
                     max_wait=0):
    """
    Do a full synchronous deploy of all project contracts or a subset of the
    contracts.

    1. Wait for whatever block number was specified (in
    """
    _deployed_contracts = {}
    _receipts = {}

    if constructor_args is None:
        constructor_args = {}

    if transaction_defaults is None:
        transaction_defaults = {}

    if contracts_to_deploy is None:
        contracts_to_deploy = tuple(all_contracts.keys())

    # Validate that all contracts are deployable meaning they have `code`
    # associated with them.
    undeployable_contracts = [
        contract_name
        for contract_name in contracts_to_deploy
        if remove_0x_prefix(all_contracts[contract_name].get('code')) is None
    ]

    if undeployable_contracts:
        raise ValueError("Some contracts do not have any

    # Extract and dependencies that exist due to library linking.
    dependency_graph = get_dependency_graph(contracts)

    # If a subset of contracts have been specified to be deployed compute
    # any dependencies that also need to be deployed.
    all_contracts_to_deploy = set(itertools.chain.from_iterable(
        get_all_contract_dependencies(contract_name, dependency_graph)
        for contract_name in contracts_to_deploy
    ))

    # Now compute the order that the contracts should be deployed based on
    # their dependencies.
    deploy_order = [
        (contract_name, all_contracts[contract_name])
        for contract_name
        in get_contract_deploy_order(dependency_graph)
        if contract_name in all_contracts_to_deploy
    ]

    # If there are any dependencies either explicit or from libraries, sort the
    # contracts by their dependencies.

    if from_address is None:
        from_address = web3.eth.defaultAccount or web3.eth.coinbase

    for contract_name, contract_data in deploy_order:
        # if the contract has dependencies then link the code.
        if dependency_graph[contract_name]:
            # TODO: link against the already deployed contracts
            assert False
        else:
            code = contract_data['code']

        if contracts_to_deploy and contract_name not in contracts_to_deploy:
            continue

        args = constructor_args.get(contract_name, None)
        if callable(args):
            args = args(_deployed_contracts)

        if deploy_gas is None:
            deploy_gas_limit = int(deploy_client.get_max_gas() * 0.98)
        elif callable(deploy_gas):
            deploy_gas_limit = deploy_gas(contract_name, contract_class)
        else:
            deploy_gas_limit = deploy_gas

        if contract_name in linker_dependencies:
            for dependency_name in linker_dependencies[contract_name]:
                deployed_contract = _deployed_contracts[dependency_name]
                link_contract_dependency(contract_class, deployed_contract)

        txn_hash = deploy_contract(
            deploy_client,
            contract_class,
            constructor_args=args,
            _from=from_address,
            gas=deploy_gas_limit,
        )
        contract_addr = get_contract_address_from_txn(
            deploy_client,
            txn_hash,
            max_wait=max_wait,
        )
        _receipts[contract_name] = deploy_client.wait_for_transaction(
            txn_hash,
            max_wait,
        )
        _deployed_contracts[contract_name] = contract_class(
            contract_addr,
            deploy_client,
        )

    _dict = {
        '_deploy_receipts': _receipts,
        '__len__': lambda s: len(_deployed_contracts),
        '__iter__': lambda s: iter(_deployed_contracts.items()),
        '__getitem__': lambda s, k: _deployed_contracts.__getitem__[k],
    }

    _dict.update(_deployed_contracts)

    return type('deployed_contracts', (object,), _dict)()


def validate_deployed_contracts(deploy_client, deployed_contracts):
    for _, deployed_contract in deployed_contracts:
        code = deploy_client.get_code(deployed_contract._meta.address)
        if len(code) <= 2:
            raise ValueError("Looks like a contract failed to deploy")
