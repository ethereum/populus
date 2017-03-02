import itertools
import re

from eth_utils import (
    is_string,
    remove_0x_prefix,
)

from .filesystem import (
    is_under_path,
)
from .linking import (
    find_link_references,
)
from .mappings import (
    get_nested_key,
)
from .string import (
    normalize_class_name,
)


def get_contract_source_file_path(contract_data):
    compilation_target = get_nested_key(contract_data, 'metadata.settings.compilationTarget')
    assert len(compilation_target) == 1
    return tuple(compilation_target.keys())[0]


def is_project_contract(contracts_source_dir, contract_data):
    try:
        contract_source_file_path = get_contract_source_file_path(contract_data)
    except KeyError:
        # TODO: abstract contracts don't have a metadata value.  How do we handle this....
        return False
    return is_under_path(contracts_source_dir, contract_source_file_path)


def is_test_contract(tests_dir, contract_data):
    try:
        contract_source_file_path = get_contract_source_file_path(contract_data)
    except KeyError:
        # TODO: abstract contracts don't have a metadata value.  How do we handle this....
        return False
    return is_under_path(tests_dir, contract_source_file_path)


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


def construct_contract_factories(web3, contracts):
    contract_classes = {
        contract_name: create_contract_factory(web3, contract_name, contract_data)
        for contract_name, contract_data
        in contracts.items()
    }
    return package_contracts(contract_classes)


def get_shallow_dependency_graph(contracts):
    """
    Given a dictionary of compiled contract data, this returns a *shallow*
    dependency graph of each contracts explicit link dependencies.
    """
    link_dependencies = {
        contract_name: set(ref.full_name for ref in find_link_references(
            contract_data['bytecode'],
            contracts.keys(),
        ))
        for contract_name, contract_data
        in contracts.items()
        if is_string(contract_data.get('bytecode'))
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


def verify_contract_bytecode(web3, ContractFactory, address):
    """
    TODO: write tests for this.
    """
    from populus.contracts.exceptions import BytecodeMismatch

    # Check that the contract has bytecode
    if ContractFactory.bytecode_runtime in EMPTY_BYTECODE_VALUES:
        raise ValueError(
            "Contract instances which contain an address cannot have empty "
            "runtime bytecode"
        )

    chain_bytecode = web3.eth.getCode(address)

    if chain_bytecode in EMPTY_BYTECODE_VALUES:
        raise BytecodeMismatch(
            "No bytecode found at address: {0}".format(address)
        )
    elif not compare_bytecode(chain_bytecode, ContractFactory.bytecode_runtime):
        raise BytecodeMismatch(
            "Bytecode found at {0} does not match compiled bytecode:\n"
            " - chain_bytecode: {1}\n"
            " - compiled_bytecode: {2}".format(
                address,
                chain_bytecode,
                ContractFactory.bytecode_runtime,
            )
        )
