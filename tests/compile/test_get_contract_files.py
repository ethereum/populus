import os

from populus.compilation import find_project_contracts


def test_gets_correct_files():
    project_dir = "tests/utility/projects/test-01/"
    file_names = find_project_contracts(project_dir)

    should_match = {
        'MutanContract.mu',
        'SerpentContract.se',
        'LLLContract.lll',
        'SolidityContract.sol',
    }

    should_not_match = {
        'BackedUpContract.sol.bak',
        'Swapfile.sol.swp',
        'not-contract.txt',
    }

    for file_name in file_names:
        assert os.path.exists(file_name)
        assert os.path.basename(file_name) in should_match
        assert os.path.basename(file_name) not in should_not_match
