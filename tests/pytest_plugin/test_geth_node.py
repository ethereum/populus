import os
import time

import pytest

from populus.geth import (
    ensure_account_exists,
    is_geth_available,
)
from eth_rpc_client import Client


skip_if_no_geth = pytest.mark.skipif(
    not is_geth_available(),
    reason="'geth' not available",
)


BASE_DIR= os.path.abspath(os.path.dirname(__file__))

geth_project_dir = os.path.join(BASE_DIR, 'projects', 'test-01')


@pytest.fixture(autouse=True)
def project_test01_dir(monkeypatch):
    monkeypatch.chdir(geth_project_dir)
    return geth_project_dir


@skip_if_no_geth
def test_geth_node_as_fixture(geth_coinbase, geth_node, project_test01_dir):
    rpc_client = Client('127.0.0.1', geth_node.rpc_port)
    block_number = rpc_client.get_block_number()
    start = time.time()
    while time.time() < start + 5:
        if rpc_client.get_block_number() > block_number:
            break
        else:
            time.sleep(0.2)
    assert rpc_client.get_block_number() > block_number
