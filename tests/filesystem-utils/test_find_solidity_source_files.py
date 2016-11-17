import os

from populus import Project
from populus.utils.filesystem import (
    mkdir,
    find_solidity_source_files,
    is_same_path,
)


def test_gets_correct_files_default_dir(project_dir, write_project_file):
    project = Project()
    file_names = find_solidity_source_files(project.contracts_source_dir)

    should_match = {
        'contracts/SolidityContract.sol',
        'contracts/AnotherFile.sol',
    }

    should_not_match = {
        'contracts/BackedUpContract.sol.bak',
        'contracts/Swapfile.sol.swp',
        'contracts/not-contract.txt',
    }

    for filename in should_match:
        write_project_file(filename)

    for filename in should_not_match:
        write_project_file(filename)

    for file_name in file_names:
        assert os.path.exists(file_name)
        assert any(is_same_path(file_name, path) for path in should_match)
        assert not any(is_same_path(file_name, path) for path in should_not_match)
