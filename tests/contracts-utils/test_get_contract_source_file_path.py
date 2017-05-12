import os

from populus.utils.contracts import (
    get_contract_source_file_path,
)
from populus.utils.filesystem import (
    is_same_path,
)
from populus.utils.testing import (
    load_contract_fixture,
    load_test_contract_fixture,
)


@load_contract_fixture('Math.sol')
def test_getting_source_file_for_project_contract(project):
    source_file_path = get_contract_source_file_path(project.compiled_contract_data['contracts']['Math'])
    expected_path = os.path.join(project.contracts_source_dir, 'Math.sol')
    assert is_same_path(source_file_path, expected_path)


@load_contract_fixture('Multiply13.sol')
@load_contract_fixture('Library13.sol')
def test_getting_source_file_for_project_contract_with_library_dependency(project):
    source_file_path = get_contract_source_file_path(project.compiled_contract_data['contracts']['Multiply13'])
    expected_path = os.path.join(project.contracts_source_dir, 'Multiply13.sol')
    assert is_same_path(source_file_path, expected_path)
