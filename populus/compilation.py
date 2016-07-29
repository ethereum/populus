import os
import json

from populus.utils.filesystem import (
    get_contracts_dir,
    get_compiled_contracts_destination_path,
    recursive_find_files,
)
from solc import (
    compile_files,
)


def find_project_contracts(project_dir):
    contracts_dir = get_contracts_dir(project_dir)

    return tuple(
        os.path.relpath(p) for p in recursive_find_files(contracts_dir, "*.sol")
    )


def write_compiled_sources(project_dir, compiled_sources):
    compiled_contract_path = get_compiled_contracts_destination_path(project_dir)

    with open(compiled_contract_path, 'w') as outfile:
        outfile.write(
            json.dumps(compiled_sources,
                       sort_keys=True,
                       indent=4,
                       separators=(',', ': '))
        )
    return compiled_contract_path


def compile_project_contracts(project_dir, **compiler_kwargs):
    contract_source_paths = find_project_contracts(project_dir)
    compiled_sources = compile_files(contract_source_paths, **compiler_kwargs)

    return contract_source_paths, compiled_sources


def compile_and_write_contracts(project_dir, **compiler_kwargs):
    contract_source_paths, compiled_sources = compile_project_contracts(
        project_dir,
        **compiler_kwargs
    )

    output_file_path = write_compiled_sources(project_dir, compiled_sources)
    return contract_source_paths, compiled_sources, output_file_path
