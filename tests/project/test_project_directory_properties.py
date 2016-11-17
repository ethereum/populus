from populus.project import Project
from populus.utils.filesystem import (
    get_contracts_dir,
    get_blockchains_dir,
    is_same_path,
)
from populus.utils.geth import (
    get_data_dir,
    get_chaindata_dir,
    get_geth_ipc_path,
)


def test_project_directory_properties(project_dir):
    project = Project()

    contracts_dir = get_contracts_dir(project_dir)
    assert is_same_path(project.contracts_dir, contracts_dir)

    blockchains_dir = get_blockchains_dir(project_dir)
    assert is_same_path(project.blockchains_dir, blockchains_dir)

    data_dir = get_data_dir(project_dir, 'some-test-chain-name')
    assert is_same_path(project.get_blockchain_data_dir('some-test-chain-name'), data_dir)

    chaindata_dir = get_chaindata_dir(data_dir)
    assert is_same_path(project.get_blockchain_chaindata_dir('some-test-chain-name'), chaindata_dir)

    geth_ipc_path = get_geth_ipc_path(data_dir)
    assert is_same_path(project.get_blockchain_ipc_path('some-test-chain-name'), geth_ipc_path)
