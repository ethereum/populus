import os
import shutil
import json
import socket
import time
import signal
import operator
import functools
import itertools


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


def get_contract_address_from_txn(blockchain_client, txn_hash, max_wait=0):
    txn_receipt = blockchain_client.wait_for_transaction(txn_hash, max_wait)

    return txn_receipt['contractAddress']


def merge_dependencies(*dependencies):
    """
    Takes dictionaries of key => set(...) and merges them all into a single
    dictionary where each key is the union of all of the sets for that key
    across all dictionaries.
    """
    return {
        k: set(functools.reduce(
            operator.or_,
            (d.get(k, set()) for d in dependencies)
        ))
        for k in itertools.chain.from_iterable((d.keys() for d in dependencies))
    }


def get_dependencies(contract_name, dependencies):
    return set(itertools.chain(
        dependencies.get(contract_name, set()), *(
            get_dependencies(dep, dependencies)
            for dep in dependencies.get(contract_name, set())
        )
    ))
