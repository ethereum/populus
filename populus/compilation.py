import os
import json

from solc import (
    compile_files,
)
from solc.exceptions import (
    ContractsNotFound,
)

from populus.utils.filesystem import (
    get_compiled_contracts_file_path,
    recursive_find_files,
    DEFAULT_CONTRACTS_DIR
)
from populus.utils.compile import (
    process_compiler_output,
)


def find_project_contracts(project_dir, contracts_rel_dir=DEFAULT_CONTRACTS_DIR):
    contracts_dir = os.path.join(project_dir, contracts_rel_dir)

    return tuple(
        os.path.relpath(p) for p in recursive_find_files(contracts_dir, "*.sol")
    )


def write_compiled_sources(project_dir, compiled_sources):
    compiled_contract_path = get_compiled_contracts_file_path(project_dir)

    with open(compiled_contract_path, 'w') as outfile:
        outfile.write(
            json.dumps(compiled_sources,
                       sort_keys=True,
                       indent=4,
                       separators=(',', ': '))
        )
    return compiled_contract_path


DEFAULT_COMPILER_OUTPUT_VALUES = ['bin', 'bin-runtime', 'abi', 'metadata']


def compile_project_contracts(project_dir, contracts_dir, compiler_settings=None):
    if compiler_settings is None:
        compiler_settings = {}

    compiler_settings.setdefault('output_values', DEFAULT_COMPILER_OUTPUT_VALUES)
    contract_source_paths = find_project_contracts(project_dir, contracts_dir)
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


def compile_and_write_contracts(project_dir, contracts_dir, compiler_settings=None):
    contract_source_paths, compiled_sources = compile_project_contracts(
        project_dir,
        contracts_dir,
        compiler_settings=compiler_settings,
    )

    output_file_path = write_compiled_sources(project_dir, compiled_sources)
    return contract_source_paths, compiled_sources, output_file_path
