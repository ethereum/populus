from __future__ import absolute_import

import anyconfig
import itertools
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
    to_tuple,
    is_string,
)

from populus import ASSETS_DIR
from populus.exceptions import (
    ValidationError,
)

from populus.utils.contracts import (
    compute_direct_dependency_graph,
    compute_recursive_contract_dependencies,
)
from populus.utils.deploy import (
    compute_deploy_order,
)
from populus.utils.filesystem import (
    recursive_find_files,
    ensure_file_exists,
    find_solidity_source_files,
)
from populus.utils.json import (
    normalize_object_for_json,
)


@to_tuple
def get_dir_source_paths(contracts_source_dir):
    return find_solidity_source_files(contracts_source_dir)


@to_tuple
def get_all_dirs_source_pathes(dir_paths, logger=None):

    all_source_paths = []
    for dir_path in set(dir_paths): # sliently ignore duplicates
        contract_source_paths = get_dir_source_paths(dir_path)
        if logger:
            logger.debug(
                "Found %s source files: %s",
                len(contract_source_paths),
                ", ".join(contract_source_paths),
            )
        all_source_paths.extend(contract_source_paths)
    return all_source_paths


def write_compiled_sources(compiled_contracts_asset_path, compiled_sources):
    logger = logging.getLogger('populus.compilation.write_compiled_sources')
    ensure_file_exists(compiled_contracts_asset_path)

    with open(compiled_contracts_asset_path, 'w') as outfile:
        json.dump(
            normalize_object_for_json(compiled_sources),
            outfile,
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


def normalize_contract_metadata(metadata):
    if not metadata:
        return None
    elif is_string(metadata):
        return json.loads(metadata)
    else:
        raise ValueError("Unknown metadata format '{0}'".format(metadata))


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
