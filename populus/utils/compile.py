from __future__ import absolute_import

import itertools

import anyconfig

import jsonschema

import os
import json
import logging

from toolz.functoolz import (
    partial,
    pipe,
)
from toolz.dicttoolz import (
    assoc,
)

from eth_utils import (
    add_0x_prefix,
    to_dict,
    to_tuple,
    is_string,
)

from populus import ASSETS_DIR
from populus.exceptions import (
    ValidationError,
)

from .contracts import (
    compute_direct_dependency_graph,
    compute_recursive_contract_dependencies,
)
from .deploy import (
    compute_deploy_order,
)
from .filesystem import (
    is_same_path,
    recursive_find_files,
    ensure_file_exists,
)
from .json import (
    normalize_object_for_json,
)
from .functional import (
    star_zip_return,
)
from .dependencies import (
    get_installed_dependency_locations,
    get_installed_packages_dir,
    recursive_find_installed_dependency_base_dirs,
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


EXCLUDE_INSTALLED_PACKAGES_GLOB = "./installed_packages/*"


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


@to_tuple
def get_dependency_source_paths(dependency_base_dir):
    """
    Find all of the solidity source files for the given dependency, excluding
    any of the source files that belong to any sub-dependencies.
    """
    source_files_to_exclude = recursive_find_files(
        dependency_base_dir,
        EXCLUDE_INSTALLED_PACKAGES_GLOB,
    )
    for source_file_path in find_solidity_source_files(dependency_base_dir):
        for exclude_path in source_files_to_exclude:
            if is_same_path(source_file_path, exclude_path):
                continue
        yield source_file_path


@to_tuple
def compute_import_remappings(source_paths, installed_dependency_locations):
    source_and_remapping_pairs = itertools.product(
        sorted(source_paths),
        sorted(installed_dependency_locations.items()),
    )

    for import_path, (package_name, package_source_dir) in source_and_remapping_pairs:
        yield "{import_path}:{package_name}={package_source_dir}".format(
            import_path=import_path,
            package_name=package_name,
            package_source_dir=package_source_dir,
        )


def compute_project_compilation_arguments(contracts_source_dir,
                                          installed_packages_dir):
    project_source_paths = get_project_source_paths(contracts_source_dir)

    installed_dependency_locations = get_installed_dependency_locations(
        installed_packages_dir,
    )

    project_import_remappings = compute_import_remappings(
        project_source_paths,
        installed_dependency_locations,
    )
    return project_source_paths, project_import_remappings


def compute_test_compilation_arguments(tests_dir,
                                       installed_packages_dir):
    test_source_paths = get_project_source_paths(tests_dir)

    installed_dependency_locations = get_installed_dependency_locations(
        installed_packages_dir,
    )

    test_import_remappings = compute_import_remappings(
        test_source_paths,
        installed_dependency_locations,
    )
    return test_source_paths, test_import_remappings


@star_zip_return
@to_tuple
def compute_installed_packages_compilation_arguments(installed_packages_dir):
    all_dependency_base_dirs = recursive_find_installed_dependency_base_dirs(
        installed_packages_dir,
    )

    for dependency_base_dir in all_dependency_base_dirs:
        (
            dependency_source_paths,
            dependency_import_remappings,
        ) = compute_dependency_compilation_arguments(dependency_base_dir)
        yield dependency_source_paths, dependency_import_remappings


def compute_dependency_compilation_arguments(dependency_base_dir):
    dependency_source_paths = get_dependency_source_paths(dependency_base_dir)
    dependency_installed_packages_dir = get_installed_packages_dir(dependency_base_dir)

    installed_sub_dependencies = get_installed_dependency_locations(
        dependency_installed_packages_dir,
    )

    dependency_import_remappings = compute_import_remappings(
        dependency_source_paths,
        installed_sub_dependencies,
    )
    return dependency_source_paths, dependency_import_remappings


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


def process_compiler_output(name_from_compiler, data_from_compiler):
    _, _, contract_name = name_from_compiler.rpartition(':')
    contract_data = normalize_contract_data(data_from_compiler)
    return contract_name, contract_data


def normalize_contract_metadata(metadata):
    if not metadata:
        return None
    elif is_string(metadata):
        return json.loads(metadata)
    else:
        raise ValueError("Unknown metadata format '{0}'".format(metadata))


def write_compiled_sources(compiled_contracts_asset_path, compiled_sources):
    logger = logging.getLogger('populus.compilation.write_compiled_sources')
    ensure_file_exists(compiled_contracts_asset_path)

    with open(compiled_contracts_asset_path, 'w') as compiled_contracts_asset_file:
        json.dump(
            normalize_object_for_json(compiled_sources),
            compiled_contracts_asset_file,
            sort_keys=True,
            indent=4,
            separators=(',', ': '),
        )

    logger.info(
        "> Wrote compiled assets to: %s",
        os.path.relpath(compiled_contracts_asset_path)
    )

    return compiled_contracts_asset_path


@to_tuple
def add_direct_dependencies_to_compiled_contracts(compiled_contracts):
    for contract_data in compiled_contracts:
        direct_dependencies = set(
            ref['name']
            for ref
            in itertools.chain(contract_data['linkrefs'], contract_data['linkrefs_runtime'])
        )
        yield assoc(contract_data, key='direct_dependencies', value=direct_dependencies)


@to_tuple
def add_full_dependencies_to_compiled_contracts(compiled_contracts):
    dependency_graph = compute_direct_dependency_graph(compiled_contracts)
    deploy_order = compute_deploy_order(dependency_graph)

    for contract_data in compiled_contracts:
        full_dependencies = compute_recursive_contract_dependencies(
            contract_data['name'],
            dependency_graph,
        )
        ordered_full_dependencies = tuple(
            contract_name
            for contract_name
            in deploy_order
            if contract_name
            in full_dependencies
        )
        yield pipe(
            contract_data,
            partial(assoc, key='full_dependencies', value=full_dependencies),
            partial(assoc, key='ordered_full_dependencies', value=ordered_full_dependencies),
        )


def post_process_compiled_contracts(compiled_contracts):
    return pipe(
        compiled_contracts,
        add_direct_dependencies_to_compiled_contracts,
        add_full_dependencies_to_compiled_contracts,
    )


def load_json_if_string(value):
    if is_string(value):
        return json.loads(value)
    else:
        return value


V1 = 'v1'


CONTRACT_DATA_SCHEMA_PATHS = {
    V1: os.path.join(ASSETS_DIR, 'contract-data.v1.schema.json'),
}


def validate_compiled_contracts(compiled_contracts, schema_version=V1):
    validation_errors = tuple(
        (
            contract_data['name'],
            get_contract_data_validation_errors(contract_data),
        )
        for contract_data
        in compiled_contracts
    )
    if validation_errors and any(tuple(zip(*validation_errors))[1]):
        error_messages_by_contract = tuple(
            (contract_name, "\n".join((error.message for error in errors)))
            for contract_name, errors
            in validation_errors
            if errors
        )
        error_message = (
            "The following compiled contracts did not pass validation:\n{0}".format(
                "\n".join((
                    "--------{name}-----------\n{error_messages}".format(
                        name=name,
                        error_messages=error_messages
                    ) for name, error_messages
                    in error_messages_by_contract
                ))
            )
        )
        raise ValidationError(error_message)


def get_contract_data_validation_errors(contract_data, schema_version=V1):
    if schema_version not in CONTRACT_DATA_SCHEMA_PATHS:
        raise KeyError("No schema for version: {0} - Must be one of {1}".format(
            schema_version,
            ", ".join(sorted(CONTRACT_DATA_SCHEMA_PATHS.keys())),
        ))
    schema = anyconfig.load(CONTRACT_DATA_SCHEMA_PATHS[schema_version])
    validator = jsonschema.Draft4Validator(schema)
    normalized_contract_data = normalize_object_for_json(contract_data)
    errors = [error for error in validator.iter_errors(normalized_contract_data)]
    return errors
