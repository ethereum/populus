import json
import itertools

from solc import (
    compile_files,
    get_solc_version,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.filesystem import (
    ensure_file_exists,
)

from populus.utils.compile import (
    compute_project_compilation_arguments,
    process_compiler_output,
    get_contract_meta,
)


DEFAULT_OUTPUT_VALUES = ['bin', 'bin-runtime', 'abi', 'devdoc', 'userdoc']


def compile_project_contracts(project, compiler_settings=None):
    if compiler_settings is None:
        compiler_settings = {}

    compiler_settings.setdefault('output_values', DEFAULT_OUTPUT_VALUES)

    result = compute_project_compilation_arguments(
        project.contracts_source_dir,
        project.installed_packages_dir,
    )
    project_source_paths, package_source_paths, import_remappings = result
    all_source_paths = tuple(itertools.chain(project_source_paths, package_source_paths))

    try:
        compiled_contracts = compile_files(
            all_source_paths,
            import_remappings=import_remappings,
            **compiler_settings
        )
    except ContractsNotFound:
        return project_source_paths, {}

    solc_version = get_solc_version()
    contract_meta = get_contract_meta(compiler_settings, solc_version)

    normalized_compiled_contracts = dict(
        process_compiler_output(contract_name, contract_data, contract_meta)
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
