import json

from solc import (
    compile_files,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.compile import (
    process_compiler_output,
    get_project_source_paths,
)


DEFAULT_COMPILER_OUTPUT_VALUES = ['bin', 'bin-runtime', 'abi', 'metadata']


def compile_project_contracts(project, compiler_settings=None):
    if compiler_settings is None:
        compiler_settings = {}

    compiler_settings.setdefault('output_values', DEFAULT_COMPILER_OUTPUT_VALUES)

    contract_source_paths = get_project_source_paths(project.contracts_source_dir)

    try:
        compiled_contracts = compile_files(contract_source_paths, **compiler_settings)
    except ContractsNotFound:
        return contract_source_paths, {}

    normalized_compiled_contracts = dict(
        process_compiler_output(contract_name, contract_data)
        for contract_name, contract_data
        in compiled_contracts.items()
    )

    return contract_source_paths, normalized_compiled_contracts


def compile_and_write_contracts(project, compiler_settings=None):
    contract_source_paths, compiled_sources = compile_project_contracts(
        project=project,
        compiler_settings=compiler_settings,
    )

    output_file_path = write_compiled_sources(
        project.compiled_contracts_asset_path,
        compiled_sources
    )
    return contract_source_paths, compiled_sources, output_file_path


def write_compiled_sources(compiled_contracts_asset_path, compiled_sources):
    with open(compiled_contracts_asset_path, 'w') as outfile:
        outfile.write(
            json.dumps(compiled_sources,
                       sort_keys=True,
                       indent=4,
                       separators=(',', ': '))
        )
    return compiled_contracts_asset_path
