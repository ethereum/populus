from __future__ import absolute_import

import itertools
import logging
import os
import pprint

from solc import (
    compile_files,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.compile import (
    process_compiler_output,
    get_project_source_paths,
    get_test_source_paths,
)


DEFAULT_COMPILER_OUTPUT_VALUES = ['abi', 'bin', 'bin-runtime', 'devdoc', 'metadata', 'userdoc']


def compile_project_contracts(project, compiler_settings=None):
    logger = logging.getLogger('populus.compilation.compile_project_contracts')

    if compiler_settings is None:
        compiler_settings = {}

    compiler_settings.setdefault('output_values', DEFAULT_COMPILER_OUTPUT_VALUES)
    logger.debug("Compiler Settings: %s", pprint.pformat(compiler_settings))

    project_contract_source_paths = get_project_source_paths(project.contracts_source_dir)
    logger.debug(
        "Found %s project source files: %s",
        len(project_contract_source_paths),
        project_contract_source_paths,
    )

    test_contract_source_paths = get_test_source_paths(project.tests_dir)
    logger.debug(
        "Found %s test source files: %s",
        len(test_contract_source_paths),
        test_contract_source_paths,
    )

    all_source_paths = tuple(itertools.chain(
        project_contract_source_paths,
        test_contract_source_paths,
    ))

    try:
        compiled_contracts = compile_files(all_source_paths, **compiler_settings)
    except ContractsNotFound:
        return all_source_paths, {}

    normalized_compiled_contracts = dict(
        process_compiler_output(contract_name, contract_data)
        for contract_name, contract_data
        in compiled_contracts.items()
    )

    logger.info("> Found %s contract source files", len(all_source_paths))
    for path in all_source_paths:
        logger.info("  - %s", os.path.relpath(path))

    logger.info("> Compiled %s contracts", len(normalized_compiled_contracts))
    for contract_name in sorted(normalized_compiled_contracts.keys()):
        logger.info("  - %s", contract_name)

    return all_source_paths, normalized_compiled_contracts
