import os
import json

from eth_utils import (
    add_0x_prefix,
    is_string,
    to_dict,
    to_tuple,
)

from .filesystem import (
    recursive_find_files,
)


DEFAULT_CONTRACTS_DIR = "./contracts/"


def get_contracts_source_dir(project_dir):
    contracts_source_dir = os.path.join(project_dir, DEFAULT_CONTRACTS_DIR)
    return os.path.abspath(contracts_source_dir)


BUILD_ASSET_DIR = "./build"


def get_build_asset_dir(project_dir):
    build_asset_dir = os.path.join(project_dir, BUILD_ASSET_DIR)
    return build_asset_dir


COMPILED_CONTRACTS_ASSET_FILENAME = './contracts.json'


def get_compiled_contracts_asset_path(build_asset_dir):
    compiled_contracts_asset_path = os.path.join(
        build_asset_dir,
        COMPILED_CONTRACTS_ASSET_FILENAME,
    )
    return compiled_contracts_asset_path


@to_tuple
def find_solidity_source_files(base_dir):
    return (
        os.path.relpath(source_file_path)
        for source_file_path
        in recursive_find_files(base_dir, "*.sol")
    )


def get_project_source_paths(contracts_source_dir):
    project_source_paths = find_solidity_source_files(contracts_source_dir)
    return project_source_paths


def get_test_source_paths(tests_dir):
    test_source_paths = find_solidity_source_files(tests_dir)
    return test_source_paths


def process_compiler_output(name_from_compiler, data_from_compiler):
    # TODO: use the source path.
    _, _, contract_name = name_from_compiler.rpartition(':')
    contract_data = normalize_contract_data(data_from_compiler)
    return contract_name, contract_data


def _load_json_if_string(value):
    if is_string(value):
        return json.loads(value)
    else:
        return value


@to_dict
def normalize_contract_data(contract_data):
    if 'metadata' in contract_data:
        yield 'metadata', normalize_contract_metadata(contract_data['metadata'])
    if 'bin' in contract_data:
        yield 'bytecode', add_0x_prefix(contract_data['bin'])
    if 'bin-runtime' in contract_data:
        yield 'bytecode_runtime', add_0x_prefix(contract_data['bin-runtime'])
    if 'abi' in contract_data:
        yield 'abi', _load_json_if_string(contract_data['abi'])
    if 'userdoc' in contract_data:
        yield 'userdoc', _load_json_if_string(contract_data['userdoc'])
    if 'devdoc' in contract_data:
        yield 'devdoc', _load_json_if_string(contract_data['devdoc'])


@to_dict
def normalize_contract_metadata(metadata):
    if not metadata:
        return None
    elif is_string(metadata):
        return json.loads(metadata)
    else:
        raise ValueError("Unknown metadata format '{0}'".format(metadata))
