import json
import itertools

from solc import (
    compile_files,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.compile import (
    compute_project_compilation_arguments,
    compute_test_compilation_arguments,
    compute_installed_packages_compilation_arguments,
    process_compiler_output,
)
from populus.utils.filesystem import (
    ensure_file_exists,
)


DEFAULT_COMPILER_OUTPUT_VALUES = ['abi', 'bin', 'bin-runtime', 'devdoc', 'metadata', 'userdoc']


def compile_project_contracts(project, compiler_settings=None):
    if compiler_settings is None:
        compiler_settings = {}

    compiler_settings.setdefault('output_values', DEFAULT_COMPILER_OUTPUT_VALUES)

    project_source_paths, project_import_remappings = compute_project_compilation_arguments(
        project.contracts_source_dir,
        project.installed_packages_dir,
    )
    test_source_paths, test_import_remappings = compute_test_compilation_arguments(
        project.tests_dir,
        project.installed_packages_dir,
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

    all_source_paths = tuple(itertools.chain(
        project_source_paths,
        test_source_paths,
        *installed_packages_source_paths
    ))
    all_import_remappings = tuple(itertools.chain(
        project_import_remappings,
        test_import_remappings,
        *installed_packages_import_remappings
    ))

    try:
        compiled_contracts = compile_files(
            all_source_paths,
            import_remappings=all_import_remappings,
            **compiler_settings
        )
    except ContractsNotFound:
        return project_source_paths, {}

    normalized_compiled_contracts = dict(
        process_compiler_output(contract_name, contract_data)
        for contract_name, contract_data
        in compiled_contracts.items()
    )

    return project_source_paths, normalized_compiled_contracts


def write_compiled_sources(compiled_contracts_asset_path, contract_data):
    ensure_file_exists(compiled_contracts_asset_path)

    with open(compiled_contracts_asset_path, 'w') as compiled_contracts_asset_file:
        json.dump(
            contract_data,
            compiled_contracts_asset_file,
            sort_keys=True,
            indent=2,
            separators=(',', ': '),
        )
    return compiled_contracts_asset_path
