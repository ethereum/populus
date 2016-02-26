import itertools
import copy
import toposort
import re

from eth_contract import Contract

from populus.utils import (
    get_contract_address_from_txn,
    merge_dependencies,
    get_dependencies,
    strip_0x_prefix,
)


def deploy_contract(rpc_client, contract_class, constructor_args=None, **kwargs):
    if 'data' in kwargs:
        raise ValueError("Cannot supply `data` for contract deployment")

    if constructor_args is None:
        constructor_args = []

    kwargs['data'] = contract_class.get_deploy_data(*constructor_args)
    txn_hash = rpc_client.send_transaction(**kwargs)
    return txn_hash


DEPENDENCY_RE = re.compile((
    r''
    '__'  # Prefixed by double underscore
    '(?P<name>[A-Za-z0-9_]{0,36}[A-Za-z0-9])'  # capture the name of the dependency
    '_{1,37}'  # and then enough underscores to finish out the 40 chars.
))


def get_linker_dependencies(contracts):
    dependencies = {
        contract_name: set(DEPENDENCY_RE.findall(contract_meta._config.code))
        for contract_name, contract_meta
        in contracts
        if '__' in contract_meta._config.code
    }
    return dependencies


def link_contract_dependency(contract, deployed_contract):
    location_re = re.compile(
        deployed_contract._config.name.ljust(38, "_").rjust(40, "_"),
    )
    contract._config.code = location_re.sub(
        strip_0x_prefix(deployed_contract._meta.address),
        contract._config.code,
    )
    return contract


def deploy_contracts(deploy_client,
                     contracts,
                     deploy_at_block=0,
                     max_wait_for_deploy=0,
                     from_address=None,
                     max_wait=0,
                     contracts_to_deploy=None,
                     dependencies=None,
                     constructor_args=None,
                     deploy_gas=None):
    _deployed_contracts = {}
    _receipts = {}

    if constructor_args is None:
        constructor_args = {}

    if dependencies is None:
        dependencies = {}

    # Potentiall wait until we've reached a specific block.
    deploy_client.wait_for_block(deploy_at_block, max_wait_for_deploy)

    # Extract and dependencies that exist due to library linking.
    linker_dependencies = get_linker_dependencies(contracts)
    deploy_dependencies = merge_dependencies(
        dependencies, linker_dependencies,
    )

    # If a subset of contracts have been specified to be deployed, compute
    # their dependencies as well.
    contracts_to_deploy = set(itertools.chain.from_iterable(
        get_dependencies(contract_name, deploy_dependencies)
        for contract_name in (contracts_to_deploy or [])
    )).union(contracts_to_deploy)

    # If there are any dependencies either explicit or from libraries, sort the
    # contracts by their dependencies.
    if deploy_dependencies:
        dependencies = copy.copy(deploy_dependencies)
        for contract_name, _ in contracts:
            if contract_name not in deploy_dependencies:
                dependencies[contract_name] = set()
        sorted_contract_names = toposort.toposort_flatten(dependencies)
        contracts = sorted(contracts, key=lambda c: sorted_contract_names.index(c[0]))

    if from_address is None:
        from_address = deploy_client.get_coinbase()

    for contract_name, contract_class in contracts:
        # If a subset of contracts have been specified, only deploy those or
        # the contracts they depend upon.
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


def package_contracts(contracts):
    contract_classes = {
        name: Contract(contract_meta, name) for name, contract_meta in contracts.items()
    }

    _dict = {
        '__len__': lambda s: len(contract_classes),
        '__iter__': lambda s: iter(contract_classes.items()),
        '__getitem__': lambda s, k: contract_classes.__getitem__[k],
    }
    _dict.update(contract_classes)

    return type('contracts', (object,), _dict)()
