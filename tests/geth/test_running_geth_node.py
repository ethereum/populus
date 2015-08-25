import os
import time

import pytest

from eth_rpc_client import Client

from populus.geth import (
    run_geth_node,
    get_geth_data_dir,
)


PROJECTS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'projects')


@pytest.fixture
def project_test04(monkeypatch):
    project_dir = os.path.join(PROJECTS_DIR, 'test-04')
    monkeypatch.chdir(project_dir)
    return project_dir


def test_running_node(project_test04):
    data_dir = get_geth_data_dir(project_test04, 'default')

    proc = run_geth_node(data_dir, rpc_port="8547")
    rpc_client = Client('127.0.0.1', port="8547")
    coinbase = rpc_client.get_coinbase()
    proc.terminate()
    assert coinbase == '0xae71658b3ab452f7e4f03bda6f777b860b2e2ff2'


def test_running_node_and_mining(project_test04):
    data_dir = get_geth_data_dir(project_test04, 'default')

    proc = run_geth_node(data_dir, rpc_port="8547", mine=True)
    rpc_client = Client('127.0.0.1', port="8547")
    block_num = rpc_client.get_block_number()
    time.sleep(5)
    start = time.time()
    while time.time() < start + 5:
        time.sleep(0.2)
        if rpc_client.get_block_number() > block_num:
            break
    proc.terminate()
    stdoutdata, stderrdata = proc.communicate()
    import ipdb; ipdb.set_trace()
    assert block_num < rpc_client.get_block_number()
