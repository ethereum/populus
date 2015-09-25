import itertools
import glob
import os
import json
import functools

from populus.utils import (
    get_contracts_dir,
    get_build_dir,
)
from populus.solidity import solc


def find_project_contracts(project_dir):
    contracts_dir = get_contracts_dir(project_dir)
    # TODO: support non-solidity based contract compilation.
    solidity_glob = os.path.join(contracts_dir, "*.sol")
    serpent_glob = os.path.join(contracts_dir, "*.se")
    lll_glob = os.path.join(contracts_dir, "*.lll")
    mutan_glob = os.path.join(contracts_dir, "*.mutan")

    return tuple(itertools.chain(
        glob.glob(solidity_glob),
        glob.glob(serpent_glob),
        glob.glob(lll_glob),
        glob.glob(mutan_glob),
    ))


def get_compiled_contract_destination_path(project_dir):
    build_dir = get_build_dir(project_dir)
    file_path = os.path.join(build_dir, 'contracts.json')
    return file_path


def write_compiled_sources(project_dir, compiled_sources):
    file_path = get_compiled_contract_destination_path(project_dir)
    with open(file_path, 'w') as outfile:
        outfile.write(
            json.dumps(compiled_sources, sort_keys=True, indent=4, separators=(',', ': '))
        )
    return file_path


def get_compiler_for_file(file_path):
    _, _, ext = file_path.rpartition('.')

    if ext == 'sol':
        return solc
    elif ext == 'lll':
        raise ValueError("Compilation of LLL contracts is not yet supported")
    elif ext == 'mu':
        raise ValueError("Compilation of LLL contracts is not yet supported")
    elif ext == 'se':
        raise ValueError("Compilation of LLL contracts is not yet supported")

    raise ValueError("Unknown contract extension {0}".format(ext))


def compile_source_file(source_path, **compiler_kwargs):
    compiler = get_compiler_for_file(source_path)

    with open(source_path) as source_file:
        source_code = source_file.read()

    # TODO: solidity specific
    compiled_source = compiler(source_code, **compiler_kwargs)
    return compiled_source


def compile_project_contracts(contracts_dir, filters=None, **compiler_kwargs):
    compiled_sources = {}

    for source_path in contracts_dir:
        compiled_source = compile_source_file(source_path, **compiler_kwargs)

        if filters:
            for contract_name, contract_data in compiled_source.items():
                if any(f(source_path, contract_name) for f in filters):
                    compiled_sources[contract_name] = contract_data
        else:
            compiled_sources.update(compiled_source)

    return compiled_sources


def check_if_matches_filter(file_path_filter, contract_filter, file_path, contract_name):
    if file_path_filter == contract_filter:
        allow_either = True
    else:
        allow_either = False

    file_path_match = all((
        file_path.endswith(file_path_filter),  # Same path
        os.path.basename(file_path_filter) == os.path.basename(file_path),  # same filename
    ))
    name_match = contract_filter == contract_name

    if file_path_match and name_match:
        return True
    elif allow_either and (file_path_match or name_match):
        return True
    else:
        return False


def generate_filter(filter_text):
    """
    Takes one of the following formats.

    * `ContractName`
    * `path/to/contractFile.sol`
    * `path/to/contractFile.sol:ContractName`

    and Returns callables that return `True` if the contract should be included.
    """
    if ':' in filter_text:
        file_path_filter, _, contract_filter = filter_text.partition(':')
    else:
        file_path_filter = contract_filter = filter_text

    return functools.partial(check_if_matches_filter, file_path_filter, contract_filter)


def get_contract_filters(*contracts):
    """
    Generate the filter functions for contract compilation.
    """
    return [generate_filter(filter_text) for filter_text in contracts]


def compile_and_write_contracts(project_dir, *contracts, **compiler_kwargs):
    filters = get_contract_filters(*contracts)
    contract_source_paths = find_project_contracts(project_dir)

    compiled_sources = compile_project_contracts(contract_source_paths, filters, **compiler_kwargs)

    output_file_path = write_compiled_sources(project_dir, compiled_sources)
    return contract_source_paths, compiled_sources, output_file_path
