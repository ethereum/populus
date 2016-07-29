import os

from populus.utils.filesystem import (
    ensure_path_exists,
)
from populus.utils.chain import (
    get_data_dir,
    get_chaindata_dir,
    get_dapp_dir,
    get_nodekey_path,
    get_geth_ipc_path,
)
from populus.chain import (
    reset_chain,
)


def test_reset_chain_on_empty_project_dir(project_dir):
    data_dir = get_data_dir(project_dir, 'test-chain')

    chaindata_dir = get_chaindata_dir(data_dir)
    dapp_dir = get_dapp_dir(data_dir)
    nodekey_path = get_nodekey_path(data_dir)
    geth_ipc_path = get_geth_ipc_path(data_dir)

    # sanity check
    assert not os.path.exists(chaindata_dir)
    assert not os.path.exists(dapp_dir)
    assert not os.path.exists(nodekey_path)
    assert not os.path.exists(geth_ipc_path)

    reset_chain(data_dir)

    # sanity check
    assert not os.path.exists(chaindata_dir)
    assert not os.path.exists(dapp_dir)
    assert not os.path.exists(nodekey_path)
    assert not os.path.exists(geth_ipc_path)


def test_reset_chain(project_dir, write_project_file):
    data_dir = get_data_dir(project_dir, 'test-chain')

    chaindata_dir = get_chaindata_dir(data_dir)
    dapp_dir = get_dapp_dir(data_dir)
    nodekey_path = get_nodekey_path(data_dir)
    geth_ipc_path = get_geth_ipc_path(data_dir)

    ensure_path_exists(chaindata_dir)
    ensure_path_exists(dapp_dir)
    write_project_file(nodekey_path)
    write_project_file(geth_ipc_path)

    # sanity check
    assert os.path.exists(chaindata_dir)
    assert os.path.exists(dapp_dir)
    assert os.path.exists(nodekey_path)
    assert os.path.exists(geth_ipc_path)

    reset_chain(data_dir)

    # sanity check
    assert not os.path.exists(chaindata_dir)
    assert not os.path.exists(dapp_dir)
    assert not os.path.exists(nodekey_path)
    assert not os.path.exists(geth_ipc_path)
