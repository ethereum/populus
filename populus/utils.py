import os
import json


CONTRACTS_DIR = "./contracts/"


def get_contracts_dir(project_dir):
    contracts_dir = os.path.join(project_dir, CONTRACTS_DIR)
    return os.path.abspath(contracts_dir)


BUILD_DIR = "./build/"


def ensure_path_exists(dir_path):
    """
    Make sure that a path exists
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


def get_build_dir(project_dir):
    build_dir_path = os.path.join(project_dir, BUILD_DIR)
    ensure_path_exists(build_dir_path)
    return build_dir_path


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


def is_executable_available(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.dirname(program)
    if fpath:
        if is_exe(program):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True

    return False
