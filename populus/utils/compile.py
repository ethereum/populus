from __future__ import absolute_import

import os
import json
import logging

from eth_utils import (
    to_tuple,
)

from .filesystem import (
    recursive_find_files,
    ensure_file_exists,
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


def write_compiled_sources(compiled_contracts_asset_path, compiled_sources):
    logger = logging.getLogger('populus.compilation.write_compiled_sources')
    ensure_file_exists(compiled_contracts_asset_path)

    with open(compiled_contracts_asset_path, 'w') as outfile:
        outfile.write(
            json.dumps(compiled_sources.to_dict(),
                       sort_keys=True,
                       indent=4,
                       separators=(',', ': '))
        )

    logger.info(
        "> Wrote compiled assets to: %s",
        os.path.relpath(compiled_contracts_asset_path)
    )

    return compiled_contracts_asset_path
