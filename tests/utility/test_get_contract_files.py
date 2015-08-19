import os
from populus.utils import get_contract_files


def test_gets_correct_files():
    project_dir = "tests/utility/projects/test-01/"
    file_names = get_contract_files(project_dir)

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
