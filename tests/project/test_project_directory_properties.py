import pytest
import sys

from populus.project import Project

from populus.utils.chains import (
    get_base_blockchain_storage_dir,
)
from populus.utils.compile import (
    get_compiled_contracts_asset_path,
    get_build_asset_dir,
    get_contracts_source_dirs,
)
from populus.utils.filesystem import (
    is_same_path,
)


def test_project_directory_properties(project_dir):
    project = Project(project_dir, create_config_file=True)

    if sys.version_info.major != 2:
        with pytest.warns(DeprecationWarning):
            project.contracts_source_dir

    contracts_source_dirs = get_contracts_source_dirs(project_dir)
    for left, right in zip(project.contracts_source_dirs, contracts_source_dirs):
        assert is_same_path(left, right)

    build_asset_dir = get_build_asset_dir(project_dir)
    assert is_same_path(project.build_asset_dir, build_asset_dir)

    compiled_contracts_asset_path = get_compiled_contracts_asset_path(build_asset_dir)
    assert is_same_path(project.compiled_contracts_asset_path, compiled_contracts_asset_path)

    base_blockchain_storage_dir = get_base_blockchain_storage_dir(project_dir)
    assert is_same_path(project.base_blockchain_storage_dir, base_blockchain_storage_dir)


def test_py_version_file_error():

    with pytest.raises(OSError):
        p = Project()  # noqa: F841
