import os
import shutil
import json
import socket
import time
import signal


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
        return True
    return False


def remove_file_if_exists(path):
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


def remove_dir_if_exists(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        return True
    return False


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


def get_open_port():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return str(port)


def wait_for_popen(proc, max_wait=5):
    wait_till = time.time() + 5
    while proc.poll() is None and time.time() < wait_till:
        time.sleep(0.1)


def kill_proc(proc):
    try:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            wait_for_popen(proc, 5)
        if proc.poll() is None:
            proc.terminate()
            wait_for_popen(proc, 2)
        if proc.poll() is None:
            proc.kill()
            wait_for_popen(proc, 1)
    except KeyboardInterrupt:
        proc.kill()


def wait_for_transaction(rpc_client, txn_hash, max_wait=60):
    start = time.time()
    while True:
        txn_receipt = rpc_client.get_transaction_receipt(txn_hash)
        if txn_receipt is not None:
            break
        elif time.time() > start + max_wait:
            raise ValueError("Could not get transaction receipt")
        time.sleep(1)
    return txn_receipt


def wait_for_block(rpc_client, block_number, max_wait=60):
    start = time.time()
    while time.time() < start + max_wait:
        if rpc_client.get_block_number() >= block_number:
            break
        time.sleep(1)
    else:
        raise ValueError("Did not reach block")


def get_contract_address_from_txn(rpc_client, txn_hash, max_wait=0):
    txn_receipt = wait_for_transaction(rpc_client, txn_hash, max_wait)

    return txn_receipt['contractAddress']
