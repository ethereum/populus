import os

from populus.utils.filesystem import (
    ensure_path_exists,
)
from populus.project import Project
from populus.utils.geth import (
    reset_chain,
)


def test_reset_chain_on_empty_project_dir(project_dir, write_project_file):
    project = Project()

    data_dir = project.get_blockchain_data_dir('test-chain')
    ensure_path_exists(data_dir)

    chaindata_dir = project.get_blockchain_chaindata_dir('test-chain')
    dapp_dir = project.get_blockchain_dapp_dir('test-chain')
    nodekey_path = project.get_blockchain_nodekey_path('test-chain')
    geth_ipc_path = project.get_blockchain_ipc_path('test-chain')

    # sanity check
    assert os.path.exists(data_dir)
    assert not os.path.exists(chaindata_dir)
    assert not os.path.exists(dapp_dir)
    assert not os.path.exists(nodekey_path)
    assert not os.path.exists(geth_ipc_path)

    reset_chain(data_dir)

    assert os.path.exists(data_dir)
    assert not os.path.exists(chaindata_dir)
    assert not os.path.exists(dapp_dir)
    assert not os.path.exists(nodekey_path)
    assert not os.path.exists(geth_ipc_path)


def test_reset_chain(project_dir, write_project_file):
    project = Project()

    data_dir = project.get_blockchain_data_dir('test-chain')
    ensure_path_exists(data_dir)

    chaindata_dir = project.get_blockchain_chaindata_dir('test-chain')
    dapp_dir = project.get_blockchain_dapp_dir('test-chain')
    nodekey_path = project.get_blockchain_nodekey_path('test-chain')
    geth_ipc_path = project.get_blockchain_ipc_path('test-chain')

    ensure_path_exists(chaindata_dir)
    ensure_path_exists(dapp_dir)
    write_project_file(nodekey_path)
    write_project_file(geth_ipc_path)

    # sanity check
    assert os.path.exists(data_dir)
    assert os.path.exists(chaindata_dir)
    assert os.path.exists(dapp_dir)
    assert os.path.exists(nodekey_path)
    assert os.path.exists(geth_ipc_path)

    reset_chain(data_dir)

    assert os.path.exists(data_dir)
    assert not os.path.exists(chaindata_dir)
    assert not os.path.exists(dapp_dir)
    assert not os.path.exists(nodekey_path)
    assert not os.path.exists(geth_ipc_path)
