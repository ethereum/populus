import os

from populus.compilation import find_project_contracts


def test_gets_correct_files(project_dir, write_project_file):
    file_names = find_project_contracts(project_dir)

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
        assert os.path.basename(file_name) in should_match
        assert os.path.basename(file_name) not in should_not_match
