from __future__ import absolute_import

import itertools
import logging
import os

from populus.utils.compile import (
    validate_compiled_contracts,
    post_process_compiled_contracts,
    compute_project_compilation_arguments,
    compute_test_compilation_arguments,
    compute_installed_packages_compilation_arguments,
)
from populus.utils.functional import (
    get_duplicates,
)


def _get_contract_key(contract_data):
    return (
        contract_data['source_path'],
        contract_data['name'],
    )


def compile_project_contracts(project):
    logger = logging.getLogger('populus.compilation.compile_project_contracts')

    project_source_paths, project_import_remappings = compute_project_compilation_arguments(
        project.contracts_source_dir,
        project.installed_packages_dir,
    )
    logger.debug(
        "Found %s project source files: %s",
        len(project_source_paths),
        project_source_paths,
    )
    test_source_paths, test_import_remappings = compute_test_compilation_arguments(
        project.tests_dir,
        project.installed_packages_dir,
    )
    logger.debug(
        "Found %s test source files: %s",
        len(test_source_paths),
        test_source_paths,
    )
    installed_packages_compilation_arguments = (
        compute_installed_packages_compilation_arguments(project.installed_packages_dir)
    )
    if installed_packages_compilation_arguments:
        installed_packages_source_paths, installed_packages_import_remappings = (
            installed_packages_compilation_arguments
        )
    else:
        installed_packages_source_paths = tuple()
        installed_packages_import_remappings = tuple()
    logger.debug(
        "Found %s dependency source files: %s",
        len(installed_packages_source_paths),
        installed_packages_source_paths,
    )

    all_source_paths = tuple(itertools.chain(
        project_source_paths,
        test_source_paths,
        *installed_packages_source_paths
    ))
    all_import_remappings = tuple(itertools.chain(
        project_import_remappings,
        test_import_remappings,
        project.config.get('compilation.import_remappings', []),
        *installed_packages_import_remappings
    ))

    compiler_backend = project.get_compiler_backend()
    base_compiled_contracts = compiler_backend.get_compiled_contracts(
        source_file_paths=all_source_paths,
        import_remappings=all_import_remappings,
    )
    compiled_contracts = post_process_compiled_contracts(base_compiled_contracts)
    validate_compiled_contracts(compiled_contracts)

    logger.info("> Found %s contract source files", len(all_source_paths))
    for path in sorted(all_source_paths):
        logger.info("  - %s", os.path.relpath(path))

    logger.info("> Compiled %s contracts", len(compiled_contracts))
    for contract_key in sorted(map(_get_contract_key, compiled_contracts)):
        logger.info("  - %s", ':'.join(contract_key))

    duplicate_contract_names = get_duplicates(
        contract_data['name']
        for contract_data
        in compiled_contracts
    )
    if duplicate_contract_names:
        raise ValueError(
            "Duplicate contract names '{0}'.  Populus cannot currently support "
            "compilation which produces multiple contracts with the same name".format(
                ", ".join(duplicate_contract_names),
            )
        )

    compiled_contracts_by_key = {
        contract_data['name']: contract_data
        for contract_data
        in compiled_contracts
    }

    return all_source_paths, compiled_contracts_by_key
