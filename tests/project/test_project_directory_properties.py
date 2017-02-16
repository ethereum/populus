from populus.project import Project
from populus.utils.filesystem import (
    is_same_path,
)
from populus.utils.contracts import (
    get_contracts_source_dir,
)


def test_project_directory_properties(project_dir):
    project = Project()

    contracts_source_dir = get_contracts_source_dir(project_dir)
    assert is_same_path(project.contracts_source_dir, contracts_source_dir)
