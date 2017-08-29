import itertools
import os

from populus import Project
from populus.compilation.helpers import (
    find_solidity_source_files,
)
from populus.utils.filesystem import (
    mkdir,
    is_same_path,
)


def test_gets_correct_files_default_dir(project, write_project_file):

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

    file_names = find_solidity_source_files(project.contracts_source_dir)


    for file_name in file_names:
        file_path = os.path.join(project.project_root_dir,file_name)
        should_path = (os.path.join(project.project_root_dir,path)
                       for path in
                       itertools.chain(should_match,['contracts/Greeter.sol'])
                       )
        should_not_path = (os.path.join(project.project_root_dir,path) for path in should_not_match)
        assert os.path.exists(file_path)
        assert any(is_same_path(file_path, path) for path in should_path)
        assert not any(is_same_path(file_path, path) for path in should_not_path)
