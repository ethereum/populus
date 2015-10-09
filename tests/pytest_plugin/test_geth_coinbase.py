import os

import pytest

from populus.geth import (
    ensure_account_exists,
    get_geth_data_dir,
    is_geth_available,
)


skip_if_no_geth = pytest.mark.skipif(
    not is_geth_available(),
    reason="'geth' not available",
)


BASE_DIR= os.path.abspath(os.path.dirname(__file__))

geth_project_dir = os.path.join(BASE_DIR, 'projects', 'test-01')
geth_chain_name = "default"


@pytest.fixture(autouse=True)
def project_test01_dir(monkeypatch):
    monkeypatch.chdir(geth_project_dir)
    return geth_project_dir


@skip_if_no_geth
def test_geth_coinbase(geth_coinbase, project_test01_dir):
    data_dir = get_geth_data_dir(project_test01_dir, 'default')
    actual_coinbase = ensure_account_exists(data_dir)
    assert geth_coinbase == actual_coinbase
