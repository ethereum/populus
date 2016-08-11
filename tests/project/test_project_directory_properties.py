from populus.project import Project
from populus.utils.filesystem import (
    get_contracts_dir,
    get_build_dir,
    get_compiled_contracts_file_path,
    get_blockchains_dir,
)
from populus.utils.chains import (
    get_data_dir,
    get_chaindata_dir,
    get_geth_ipc_path,
)


def test_project_directory_properties(project_dir):
    project = Project()

    contracts_dir = get_contracts_dir(project_dir)
    assert project.contracts_dir == contracts_dir

    build_dir = get_build_dir(project_dir)
    assert project.build_dir == build_dir

    compiled_contracts_file_path = get_compiled_contracts_file_path(project_dir)
    assert project.compiled_contracts_file_path == compiled_contracts_file_path

    blockchains_dir = get_blockchains_dir(project_dir)
    assert project.blockchains_dir == blockchains_dir

    data_dir = get_data_dir(project_dir, 'some-test-chain-name')
    assert project.get_blockchain_data_dir('some-test-chain-name') == data_dir

    chaindata_dir = get_chaindata_dir(data_dir)
    assert project.get_blockchain_chaindata_dir('some-test-chain-name') == chaindata_dir

    geth_ipc_path = get_geth_ipc_path(data_dir)
    assert project.get_blockchain_ipc_path('some-test-chain-name') == geth_ipc_path
