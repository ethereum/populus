import itertools
import logging
import os

from populus.utils.compile import (
    get_project_source_paths,
    get_test_source_paths,
)


def compile_project_contracts(project):
    logger = logging.getLogger('populus.compilation.compile_project_contracts')

    project_contract_source_paths = get_project_source_paths(project.contracts_source_dir)
    logger.debug(
        "Found %s project source files: %s",
        len(project_contract_source_paths),
        ", ".join(project_contract_source_paths),
    )

    test_contract_source_paths = get_test_source_paths(project.tests_dir)
    logger.debug(
        "Found %s test source files: %s",
        len(test_contract_source_paths),
        ", ".join(test_contract_source_paths),
    )

    all_source_paths = tuple(itertools.chain(
        project_contract_source_paths,
        test_contract_source_paths,
    ))

    compiler_backend = project.get_compiler_backend()
    compiled_contract_data = compiler_backend.get_compiled_contract_data(
        source_file_paths=all_source_paths,
        import_remappings=None,
    )

    logger.info("> Found %s contract source files", len(all_source_paths))
    for path in all_source_paths:
        logger.info("  - %s", os.path.relpath(path))

    logger.info("> Compiled %s contracts", len(compiled_contract_data))
    for contract_name in sorted(compiled_contract_data.keys()):
        logger.info("  - %s", contract_name)

    return all_source_paths, compiled_contract_data
