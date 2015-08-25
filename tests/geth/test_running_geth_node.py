import os
import time

import pytest

from eth_rpc_client import Client

from populus.utils import (
    get_open_port,
    ensure_path_exists,
)
from populus.geth import (
    run_geth_node,
    get_geth_data_dir,
    get_geth_accounts,
    reset_chain,
    ensure_account_exists,
)


PROJECTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'projects')


@pytest.fixture
def project_test04(monkeypatch):
    project_dir = os.path.join(PROJECTS_DIR, 'test-04')
    monkeypatch.chdir(project_dir)

    data_dir = get_geth_data_dir(project_dir, 'default')
    ensure_path_exists(data_dir)
    reset_chain(data_dir)

    return project_dir


@pytest.fixture
def open_port():
    return get_open_port()


def test_running_node(project_test04, open_port):
    data_dir = get_geth_data_dir(project_test04, 'default')
    ensure_account_exists(data_dir)

    command, proc = run_geth_node(data_dir, rpc_port=open_port, mine=False)
    time.sleep(2)
    rpc_client = Client('127.0.0.1', port=open_port)
    coinbase = rpc_client.get_coinbase()
    proc.terminate()
    assert coinbase == get_geth_accounts(project_test04)[0]


def test_running_node_and_mining(project_test04, open_port):
    data_dir = get_geth_data_dir(project_test04, 'default')
    ensure_account_exists(data_dir)

    command, proc = run_geth_node(data_dir, rpc_port=open_port, mine=True)
    time.sleep(2)
    rpc_client = Client('127.0.0.1', port=open_port)
    try:
        block_num = rpc_client.get_block_number()
    except Exception as arst:
        proc.terminate()
        time.sleep(1)
        arst, tsra = proc.communicate()
        import ipdb; ipdb.set_trace()
        raise
    time.sleep(5)
    start = time.time()
    while time.time() < start + 5:
        time.sleep(0.2)
        if rpc_client.get_block_number() > block_num:
            break
    assert block_num < rpc_client.get_block_number()
