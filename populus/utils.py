import os
import glob
import itertools
import json

import ethereum
from ethereum._solidity import get_solidity


CONTRACTS_DIR = "./contracts/"


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


def get_contract_files(project_dir):
    # TODO: support non-solidity based contract compilation.
    solidity_glob = os.path.join(project_dir, CONTRACTS_DIR, "*.sol")
    serpent_glob = os.path.join(project_dir, CONTRACTS_DIR, "*.se")
    lll_glob = os.path.join(project_dir, CONTRACTS_DIR, "*.lll")
    mutan_glob = os.path.join(project_dir, CONTRACTS_DIR, "*.mutan")

    return itertools.chain(
        glob.glob(solidity_glob),
        glob.glob(serpent_glob),
        glob.glob(lll_glob),
        glob.glob(mutan_glob),
    )


BUILD_DIR = "./build/"


def _ensure_build_dir(project_dir):
    """
    Make sure the build directory is present in the project.
    """
    build_dir_path = os.path.join(project_dir, BUILD_DIR)
    if not os.path.exists(build_dir_path):
        os.mkdir(build_dir_path)


def write_compiled_sources(project_dir, compiled_sources):
    _ensure_build_dir(project_dir)

    outfile_path = os.path.join(project_dir, BUILD_DIR, 'contracts.json')
    with open(outfile_path, 'w') as outfile:
        outfile.write(
            json.dumps(compiled_sources, sort_keys=True, indent=4, separators=(',', ': '))
        )


def load_contracts(project_dir):
    compiled_contracts_path = os.path.join(project_dir, BUILD_DIR, 'contracts.json')
    if not os.path.exists(compiled_contracts_path):
        raise ValueError("No compiled contracts found")

    with open(compiled_contracts_path) as contracts_file:
        contracts = json.loads(contracts_file.read())

    return contracts


def deploy_contracts(client, contracts):
    _from = client.get_coinbase()
    deployed_contracts = {}

    for name, contract in contracts.items():
        txn_hash = client.send_transaction(_from=_from, data=contract['code'])
        receipt = client.get_transaction_receipt(txn_hash)
        if receipt is None:
            contract_addr = None
        else:
            contract_addr = receipt['contractAddress']
        deployed_contracts[name] = {
            'txn': txn_hash,
            'addr': contract_addr,
        }

    return deployed_contracts
