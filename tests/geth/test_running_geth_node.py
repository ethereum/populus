import os
import time
import signal

import pytest

from eth_rpc_client import Client

from populus.utils import (
    get_open_port,
    ensure_path_exists,
    wait_for_popen,
)
from populus.geth import (
    is_geth_available,
    run_geth_node,
    get_geth_data_dir,
    get_geth_accounts,
    reset_chain,
    ensure_account_exists,
)


PROJECTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'projects')


skip_if_no_geth = pytest.mark.skipif(
    not is_geth_available(),
    reason="'geth' not available",
)


@pytest.fixture
def project_test04(monkeypatch):
    project_dir = os.path.join(PROJECTS_DIR, 'test-04')
    monkeypatch.chdir(project_dir)

    data_dir = get_geth_data_dir(project_dir, 'default')
    ensure_path_exists(data_dir)
    reset_chain(data_dir)

    ensure_account_exists(data_dir)

    return project_dir


@pytest.fixture
def open_port():
    return get_open_port()


@skip_if_no_geth
def test_running_node_without_mining(project_test04, open_port):
    data_dir = get_geth_data_dir(project_test04, 'default')

    command, proc = run_geth_node(data_dir, rpc_port=open_port, mine=False)
    wait_for_popen(proc)
    rpc_client = Client('127.0.0.1', port=open_port)
    coinbase = rpc_client.get_coinbase()
    proc.send_signal(signal.SIGINT)
    wait_for_popen(proc)
    assert coinbase == get_geth_accounts(data_dir)[0]


@skip_if_no_geth
def test_running_node_and_mining(project_test04, open_port):
    data_dir = get_geth_data_dir(project_test04, 'default')

    command, proc = run_geth_node(data_dir, rpc_port=open_port, mine=True)
    wait_for_popen(proc)
    rpc_client = Client('127.0.0.1', port=open_port)
    block_num = rpc_client.get_block_number()
    start = time.time()

    rpc_client.wait_for_block(block_num + 1, 60)

    assert block_num < rpc_client.get_block_number()
    proc.send_signal(signal.SIGINT)
    wait_for_popen(proc)
