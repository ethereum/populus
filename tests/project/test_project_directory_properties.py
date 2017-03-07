import pytest
import sys

from populus.project import Project

from populus.utils.chains import (
    get_base_blockchain_storage_dir,
)
from populus.utils.compile import (
    get_compiled_contracts_asset_path,
    get_build_asset_dir,
    get_contracts_source_dir,
)
from populus.utils.filesystem import (
    is_same_path,
)
from populus.utils.geth import (
    get_data_dir,
    get_chaindata_dir,
    get_geth_ipc_path,
)


@pytest.mark.skipif(sys.version_info.major == 2, reason="warning assertions are broken in py27")
def test_project_directory_properties(project_dir):
    project = Project()

    contracts_source_dir = get_contracts_source_dir(project_dir)
    assert is_same_path(project.contracts_source_dir, contracts_source_dir)
    with pytest.warns(DeprecationWarning):
        assert is_same_path(project.contracts_dir, contracts_source_dir)

    build_asset_dir = get_build_asset_dir(project_dir)
    assert is_same_path(project.build_asset_dir, build_asset_dir)
    with pytest.warns(DeprecationWarning):
        assert is_same_path(project.build_dir, build_asset_dir)

    compiled_contracts_asset_path = get_compiled_contracts_asset_path(build_asset_dir)
    assert is_same_path(project.compiled_contracts_asset_path, compiled_contracts_asset_path)
    with pytest.warns(DeprecationWarning):
        assert is_same_path(project.compiled_contracts_file_path, compiled_contracts_asset_path)

    base_blockchain_storage_dir = get_base_blockchain_storage_dir(project_dir)
    assert is_same_path(project.base_blockchain_storage_dir, base_blockchain_storage_dir)
    with pytest.warns(DeprecationWarning):
        assert is_same_path(project.blockchains_dir, base_blockchain_storage_dir)

    data_dir = get_data_dir(project_dir, 'some-test-chain-name')
    with pytest.warns(DeprecationWarning):
        assert is_same_path(project.get_blockchain_data_dir('some-test-chain-name'), data_dir)

    chaindata_dir = get_chaindata_dir(data_dir)
    with pytest.warns(DeprecationWarning):
        assert is_same_path(project.get_blockchain_chaindata_dir('some-test-chain-name'), chaindata_dir)

    geth_ipc_path = get_geth_ipc_path(data_dir)
    with pytest.warns(DeprecationWarning):
        assert is_same_path(project.get_blockchain_ipc_path('some-test-chain-name'), geth_ipc_path)
