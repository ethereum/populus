import json
import itertools

from solc import (
    compile_files,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.filesystem import (
    ensure_file_exists,
)
from populus.utils.compiling import (
    get_compiled_contracts_asset_path,
    compute_project_compilation_arguments,
)


DEFAULT_OUTPUT_VALUES = ['bin', 'bin-runtime', 'abi', 'devdoc', 'userdoc']


def compile_project_contracts(project,
                              **compiler_kwargs):
    compiler_kwargs.setdefault('output_values', DEFAULT_OUTPUT_VALUES)

    result = compute_project_compilation_arguments(
        project.contracts_source_dir,
        project.installed_packages_dir,
    )
    project_source_paths, package_source_paths, import_remappings = result
    all_source_paths = tuple(itertools.chain(project_source_paths, package_source_paths))

    try:
        compiled_sources = compile_files(
            all_source_paths,
            import_remappings=import_remappings,
            **compiler_kwargs
        )
    except ContractsNotFound:
        return project_source_paths, {}

    return project_source_paths, compiled_sources


def write_compiled_sources(chain_metadata_dir, contract_data):
    compiled_contracts_asset_path = get_compiled_contracts_asset_path(chain_metadata_dir)
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
