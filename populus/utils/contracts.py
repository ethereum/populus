import itertools
import re

from eth_utils import (
    remove_0x_prefix,
    to_dict,
)

from .filesystem import (
    is_under_path,
)
from .string import (
    normalize_class_name,
)


def is_project_contract(contracts_source_dirs, contract_data):
    return any(
        is_under_path(source_dir, contract_data['source_path'])
        for source_dir
        in contracts_source_dirs
    )


def is_test_contract(tests_dir, contract_data):
    return is_under_path(tests_dir, contract_data['source_path'])


def package_contracts(contract_factories):
    _dict = {
        '__len__': lambda s: len(contract_factories),
        '__iter__': lambda s: iter(contract_factories.items()),
        '__contains__': lambda s, k: contract_factories.__contains__(k),
        '__getitem__': lambda s, k: contract_factories.__getitem__(k),
        '__setitem__': lambda s, k, v: contract_factories.__setitem__(k, v),
        'keys': lambda s: contract_factories.keys(),
        'values': lambda s: contract_factories.values(),
    }
    _dict.update(contract_factories)

    return type('contracts', (object,), _dict)()


CONTRACT_FACTORY_FIELDS = {
    'abi',
    'asm',
    'ast',
    'bytecode',
    'bytecode_runtime',
    'clone_bin',
    'dev_doc',
    'interface',
    'metadata',
    'opcodes',
    'src_map',
    'src_map_runtime',
    'user_doc',
}


def create_contract_factory(web3, contract_name, contract_data):
    factory_kwargs = {
        key: contract_data[key]
        for key
        in CONTRACT_FACTORY_FIELDS
        if key in contract_data
    }
    return web3.eth.contract(
        contract_name=normalize_class_name(contract_name),
        **factory_kwargs
    )


def construct_contract_factories(web3, compiled_contracts):
    contract_classes = {
        contract_name: create_contract_factory(
            web3,
            contract_name,
            contract_data,
        )
        for contract_name, contract_data
        in compiled_contracts.items()
    }

    return package_contracts(contract_classes)


@to_dict
def compute_direct_dependency_graph(compiled_contracts):
    """
    Given a dictionary or mapping of compiled contract data, this returns a *shallow*
    dependency graph of each contracts explicit link dependencies.
    """
    for contract_data in compiled_contracts:
        yield (
            contract_data['name'],
            contract_data['direct_dependencies'],
        )


def compute_recursive_contract_dependencies(contract_name, dependency_graph):
    """
    Recursive computation of the linker dependencies for a specific contract
    within a contract dependency graph.
    """
    direct_dependencies = dependency_graph.get(contract_name, set())
    sub_dependencies = itertools.chain.from_iterable((
        compute_recursive_contract_dependencies(dep, dependency_graph)
        for dep in direct_dependencies
    ))
    return set(itertools.chain(direct_dependencies, sub_dependencies))


CONTRACT_NAME_REGEX = '^[_a-zA-Z][_a-zA-Z0-9]*$'


def is_contract_name(value):
    return bool(re.match(CONTRACT_NAME_REGEX, value))


EMPTY_BYTECODE_VALUES = {None, "0x"}


SWARM_HASH_PREFIX = "a165627a7a72305820"
SWARM_HASH_SUFFIX = "0029"
EMBEDDED_SWARM_HASH_REGEX = (
    SWARM_HASH_PREFIX +
    "[0-9a-zA-Z]{64}" +
    SWARM_HASH_SUFFIX +
    "$"
)

SWARM_HASH_REPLACEMENT = (
    SWARM_HASH_PREFIX +
    "<" +
    "-" * 20 +
    "swarm-hash-placeholder" +
    "-" * 20 +
    ">" +
    SWARM_HASH_SUFFIX
)


def compare_bytecode(left, right):
    unprefixed_left = remove_0x_prefix(left)
    unprefixed_right = remove_0x_prefix(right)

    norm_left = re.sub(EMBEDDED_SWARM_HASH_REGEX, SWARM_HASH_REPLACEMENT, unprefixed_left)
    norm_right = re.sub(EMBEDDED_SWARM_HASH_REGEX, SWARM_HASH_REPLACEMENT, unprefixed_right)

    if len(norm_left) != len(unprefixed_left) or len(norm_right) != len(unprefixed_right):
        raise ValueError(
            "Invariant.  Normalized bytecodes are not the correct lengths:" +
            "\n- left  (original)  :" +
            left, +
            "\n- left  (unprefixed):" +
            unprefixed_left +
            "\n- left  (normalized):" +
            norm_left +
            "\n- right (original)  :" +
            right +
            "\n- right (unprefixed):" +
            unprefixed_right +
            "\n- right (normalized):" +
            norm_right
        )

    return norm_left == norm_right


def verify_contract_bytecode(web3, expected_bytecode, address):
    """
    TODO: write tests for this.
    """
    from populus.contracts.exceptions import BytecodeMismatch

    # Check that the contract has bytecode
    if expected_bytecode in EMPTY_BYTECODE_VALUES:
        raise ValueError(
            "Contract instances which contain an address cannot have empty "
            "runtime bytecode"
        )

    chain_bytecode = web3.eth.getCode(address)

    if chain_bytecode in EMPTY_BYTECODE_VALUES:
        raise BytecodeMismatch(
            "No bytecode found at address: {0}".format(address)
        )
    elif not compare_bytecode(chain_bytecode, expected_bytecode):
        raise BytecodeMismatch(
            "Bytecode found at {0} does not match compiled bytecode:\n"
            " - chain_bytecode: {1}\n"
            " - compiled_bytecode: {2}".format(
                address,
                chain_bytecode,
                expected_bytecode,
            )
        )


def find_deploy_block_number(web3, address):
    chain_bytecode = web3.eth.getCode(address, "latest")
    if chain_bytecode in EMPTY_BYTECODE_VALUES:
        raise NotImplementedError("Cannot find deploy transaction for address with empty code")

    left = 0
    right = web3.eth.blockNumber

    while left + 1 < right:
        middle = (left + right) // 2
        # This only works if the node was not fast synced for the provided
        # `block_identifier`.
        try:
            middle_code = web3.eth.getCode(address, block_identifier=middle)
        except ValueError as err:
            if 'Missing trie node' in str(err):
                left = middle
                continue
            raise

        if middle_code in EMPTY_BYTECODE_VALUES:
            left = middle
        else:
            right = middle

    code_at_right = web3.eth.getCode(address, block_identifier=right)
    if code_at_right in EMPTY_BYTECODE_VALUES:
        raise ValueError(
            "Something went wrong with the binary search to find the deploy block"
        )
    code_at_previous_block = web3.eth.getCode(address, block_identifier=right - 1)
    if code_at_previous_block not in EMPTY_BYTECODE_VALUES:
        raise ValueError(
            "Something went wrong with the binary search to find the deploy block"
        )
    return right
