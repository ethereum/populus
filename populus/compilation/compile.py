import logging
import os

from .helpers import (
    get_dir_source_paths,
    post_process_compiled_contracts,
    validate_compiled_contracts,
)

from .backends.solc_auto import (
    get_compiler_backend_class_for_version
)

from populus.utils.functional import (
    get_duplicates,
)


from populus.config.loading import (
    load_global_config,
)


def _get_contract_key(contract_data):
    return (
        contract_data['source_path'],
        contract_data['name'],
    )


def compile_dirs(dir_paths,
                 global_config_path=None,
                 import_remappings=None,
                 compiler_version="auto"
                 ):

    logger = logging.getLogger('populus.compilation.helpers.compile_dir')
    if import_remappings is None:
        import_remappings = []

    all_source_paths = []
    for dir_path in set(dir_paths): # sliently ignore duplicates
        contract_source_paths = get_dir_source_paths(dir_path)
        logger.debug(
            "Found %s source files: %s",
            len(contract_source_paths),
            ", ".join(contract_source_paths),
        )
        all_source_paths.extend(contract_source_paths)

    global_config = load_global_config(global_config_path)
    compiler_backend = get_compiler_backend_class_for_version(compiler_version, global_config)

    base_compiled_contracts = compiler_backend.get_compiled_contracts(
        source_file_paths=all_source_paths,
        import_remappings=import_remappings,
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
