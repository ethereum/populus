import json

from eth_utils import (
    to_dict,
    add_0x_prefix,
    is_string,
)


def process_compiler_output(name_from_compiler, data_from_compiler):
    # TODO: use the source path.
    _, _, contract_name = name_from_compiler.rpartition(':')
    contract_data = normalize_contract_data(data_from_compiler)
    return contract_name, contract_data


@to_dict
def normalize_contract_data(contract_data):
    if 'metadata' in contract_data:
        yield 'metadata', normalize_contract_metadata(contract_data['metadata'])
    if 'bin' in contract_data:
        yield 'bytecode', add_0x_prefix(contract_data['bin'])
    if 'bin-runtime' in contract_data:
        yield 'bytecode_runtime', add_0x_prefix(contract_data['bin-runtime'])
    if 'abi' in contract_data:
        yield 'abi', contract_data['abi']
    if 'userdoc' in contract_data:
        yield 'userdoc', contract_data['userdoc']
    if 'devdoc' in contract_data:
        yield 'devdoc', contract_data['devdoc']


@to_dict
def normalize_contract_metadata(metadata):
    if is_string(metadata):
        metadata = json.loads(metadata)

    return metadata
