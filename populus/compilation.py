import itertools
import glob
import os
import json

import ethereum

from ethereum._solidity import get_solidity

from populus.utils import (
    get_contracts_dir,
    get_build_dir,
)


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


def _compile_rich(compiler, code):
    """
    Shim for the `compile_rich` functionality from `pyethereum` which is not
    currently available on pypi as of 2015-08-18
    """
    return {
        contract_name: {
            'code': "0x" + contract.get('binary'),
            'info': {
                'abiDefinition': contract.get('json-abi'),
                'compilerVersion': ethereum.__version__,
                'developerDoc': contract.get('natspec-dev'),
                'language': 'Solidity',
                'languageVersion': '0',
                'source': code,
                'userDoc': contract.get('natspec-user')
            },
        }
        for contract_name, contract
        in compiler.combined(code)
    }


def get_compiler_for_file(file_path):
    _, _, ext = file_path.rpartition('.')

    if ext == 'sol':
        compiler = get_solidity()
        if compiler is None:
            raise ValueError("No solidity compiler")
        return compiler
    elif ext == 'lll':
        raise ValueError("Compilation of LLL contracts is not yet supported")
    elif ext == 'mu':
        raise ValueError("Compilation of LLL contracts is not yet supported")
    elif ext == 'se':
        raise ValueError("Compilation of LLL contracts is not yet supported")

    raise ValueError("Unknown contract extension {0}".format(ext))


def compile_source_file(source_path):
    compiler = get_compiler_for_file(source_path)

    with open(source_path) as source_file:
        source_code = source_file.read()

    # TODO: solidity specific
    compiled_source = _compile_rich(compiler, source_code)
    return compiled_source


def compile_project_contracts(contracts_dir):
    compiled_sources = {}

    for source_path in contracts_dir:
        compiled_source = compile_source_file(source_path)
        compiled_sources.update(compiled_source)

    return compiled_sources


def compile_and_write_contracts(project_dir):
    contract_source_paths = find_project_contracts(project_dir)

    compiled_sources = compile_project_contracts(contract_source_paths)

    output_file_path = write_compiled_sources(project_dir, compiled_sources)
    return contract_source_paths, compiled_sources, output_file_path
