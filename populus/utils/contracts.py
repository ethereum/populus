import itertools
import os
import re

from .types import (
    is_string,
)
from .linking import (
    find_link_references,
)


DEFAULT_CONTRACTS_DIR = "./contracts/"


def get_contracts_source_dir(project_dir):
    contracts_source_dir = os.path.join(project_dir, DEFAULT_CONTRACTS_DIR)
    return os.path.abspath(contracts_source_dir)


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


def get_shallow_dependency_graph(contracts):
    """
    Given a dictionary of compiled contract data, this returns a *shallow*
    dependency graph of each contracts explicit link dependencies.
    """
    link_dependencies = {
        contract_name: set(ref.full_name for ref in find_link_references(
            contract_data['code'],
            contracts.keys(),
        ))
        for contract_name, contract_data
        in contracts.items()
        if is_string(contract_data.get('code'))
    }
    return link_dependencies


def get_recursive_contract_dependencies(contract_name, dependency_graph):
    """
    Recursive computation of the linker dependencies for a specific contract
    within a contract dependency graph.
    """
    direct_dependencies = dependency_graph.get(contract_name, set())
    sub_dependencies = itertools.chain.from_iterable((
        get_recursive_contract_dependencies(dep, dependency_graph)
        for dep in direct_dependencies
    ))
    return set(itertools.chain(direct_dependencies, sub_dependencies))


CONTRACT_NAME_REGEX = '^[_a-zA-Z][_a-zA-Z0-9]*$'


def is_contract_name(value):
    return bool(re.match(CONTRACT_NAME_REGEX, value))


EMPTY_BYTECODE_VALUES = {None, "0x"}


def verify_contract_bytecode(web3, ContractFactory, address):
    """
    TODO: write tests for this.
    """
    from populus.contracts.exceptions import BytecodeMismatch

    # Check that the contract has bytecode
    if ContractFactory.code_runtime in EMPTY_BYTECODE_VALUES:
        raise ValueError(
            "Contract instances which contain an address cannot have empty "
            "runtime bytecode"
        )

    chain_bytecode = web3.eth.getCode(address)

    if chain_bytecode in EMPTY_BYTECODE_VALUES:
        raise BytecodeMismatch(
            "No bytecode found at address: {0}".format(address)
        )
    elif chain_bytecode != ContractFactory.code_runtime:
        raise BytecodeMismatch(
            "Bytecode found at {0} does not match compiled bytecode:\n"
            " - chain_bytecode: {1}\n"
            " - compiled_bytecode: {2}".format(
                address,
                chain_bytecode,
                ContractFactory.code_runtime,
            )
        )
