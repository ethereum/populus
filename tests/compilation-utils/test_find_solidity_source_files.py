import os

from populus import Project
from populus.utils.compiling import (
    find_solidity_source_files,
)
from populus.utils.filesystem import (
    mkdir,
    is_same_path,
)


def test_gets_correct_files_default_dir(project_dir, write_project_file):
    project = Project
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


def test_gets_correct_files_custom_dir(project_dir, write_project_file):
    custom_dir = "my_custom_dir"
    mkdir(os.path.join(project_dir, custom_dir))
    file_names = find_project_contracts(project_dir, custom_dir)

    should_match = {
        '{}/SolidityContract.sol'.format(custom_dir),
        '{}/AnotherFile.sol'.format(custom_dir),
    }

    should_not_match = {
        '{}/BackedUpContract.sol.bak'.format(custom_dir),
        '{}/Swapfile.sol.swp'.format(custom_dir),
        '{}/not-contract.txt'.format(custom_dir),
    }

    for filename in should_match:
        write_project_file(filename)

    for filename in should_not_match:
        write_project_file(filename)

    for file_name in file_names:
        assert os.path.exists(file_name)
        assert os.path.basename(file_name) in should_match
        assert os.path.basename(file_name) not in should_not_match
