import os
import json

from populus.utils.filesystem import (
    get_compiled_contracts_file_path,
    recursive_find_files,
    DEFAULT_CONTRACTS_DIR
)
from solc import (
    compile_files,
)
from solc.exceptions import (
    ContractsNotFound,
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


def compile_project_contracts(project_dir, contracts_dir, **compiler_kwargs):
    compiler_kwargs.setdefault('output_values', ['bin', 'bin-runtime', 'abi'])
    contract_source_paths = find_project_contracts(project_dir, contracts_dir)
    try:
        compiled_sources = compile_files(contract_source_paths, **compiler_kwargs)
    except ContractsNotFound:
        return contract_source_paths, {}

    return contract_source_paths, compiled_sources


def compile_and_write_contracts(project_dir, contracts_dir, **compiler_kwargs):
    contract_source_paths, compiled_sources = compile_project_contracts(
        project_dir,
        contracts_dir,
        **compiler_kwargs
    )

    output_file_path = write_compiled_sources(project_dir, compiled_sources)
    return contract_source_paths, compiled_sources, output_file_path
